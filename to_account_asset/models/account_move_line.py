from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    asset_category_id = fields.Many2one('account.asset.category', string='Asset Category', help="If set, it will automatically generate the corresponding assets.")
    asset_start_date = fields.Date(string='Asset Start Date', compute='_get_asset_date', readonly=True, store=True)
    asset_end_date = fields.Date(string='Asset End Date', compute='_get_asset_date', readonly=True, store=True)
    asset_mrr = fields.Float(string='Monthly Recurring Revenue', compute='_get_asset_date', readonly=True, digits='Account', store=True)

    @api.depends('asset_category_id', 'move_id.invoice_date')
    def _get_asset_date(self):
        for r in self:
            r.asset_mrr = 0
            r.asset_start_date = False
            r.asset_end_date = False
            cat = r.asset_category_id
            if cat:
                if cat.method_number == 0 or cat.method_period == 0:
                    raise UserError(_('The number of depreciations or the period length of your asset category cannot be 0.'))
                months = cat.method_number * cat.method_period
                if r.move_id.type in ['out_invoice', 'out_refund']:
                    r.asset_mrr = r.price_subtotal / months
                if r.move_id.invoice_date:
                    start_date = r.move_id.invoice_date.replace(day=1)
                    end_date = (start_date + relativedelta(months=months, days=-1))
                    r.asset_start_date = start_date
                    r.asset_end_date = end_date

    def _prepare_asset_data(self, value, currency_id, suffix=''):
        self.ensure_one()
        analytic_account_id = self.asset_category_id.sudo().analytic_account_id
        if self.product_id and self.product_id.default_code:
            code = "[%s] %s" % (self.product_id.default_code, self.move_id.name)
        else:
            code = "[%s] %s" % (self.product_id.default_code, self.move_id.name)
        if code and suffix:
            code = "%s [%s]" % (code, suffix)
        vals = {
            'name': self.name,
            'category_id': self.asset_category_id.id or self.product_id.asset_category_id.id,
            'value': value,
            'partner_id': self.move_id.partner_id.id,
            'company_id': self.move_id.company_id.id,
            'currency_id': currency_id.id,
            'date': self.move_id.invoice_date,
            'original_move_line_ids': [(6, 0, [self.id])],
            'invoice_line_id': self.id,
            'product_id': self.product_id and self.product_id.id or False,
            'analytic_account_id': analytic_account_id and analytic_account_id.id or False,
            }
        analytic_tag_ids = self.asset_category_id.sudo().analytic_tag_ids
        if analytic_tag_ids:
            vals['analytic_tag_ids'] = [(6, 0, analytic_tag_ids.ids)]
        
        if self.asset_category_id.date_first_depreciation == 'manual':
            vals.update({
                'first_depreciation_date': self.move_id.date,
                })
        
        changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
        vals.update(changed_vals['value'])
        return vals

    def _calculate_asset_qty(self):
        return 1

    def _prepare_asset_vals_list(self):
        vals_list = []
        prec = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for r in self:
            asset_category_id = r.asset_category_id
            if asset_category_id:
                if asset_category_id.use_company_currency or not r.currency_id or r.currency_id == r.company_id.currency_id:
                    value = r.balance
                    currency_id = r.move_id.company_currency_id
                else:
                    value = r.amount_currency
                    currency_id = r.move_id.currency_id

                quantity = r._calculate_asset_qty()
                if  float_is_zero(quantity, precision_digits=prec):
                    continue
                if float_compare(quantity, 1, precision_digits=prec) <= 0:
                    vals_list.append(r._prepare_asset_data(value, currency_id))
                else:
                    qty_round = float_round(quantity, precision_digits=prec)
                    if not qty_round.is_integer():
                        qty_round = 1
                    int_qty = int(qty_round)

                    for x in range(int_qty):
                        vals_list.append(r._prepare_asset_data(value / int_qty, currency_id, suffix=str(x)))
        return vals_list

    def generate_assets(self):
        # create assets
        vals_list = self._prepare_asset_vals_list()
        if vals_list:
            assets = self.env['account.asset.asset'].create(vals_list)

            # confirm the assets whose category has Auto-Confirm Assets enabled
            assets_to_validate = assets.filtered(lambda asset: asset.category_id.open_asset)
            if assets_to_validate:
                assets_to_validate.validate()
        return True

    def action_generate_assets(self):
        return self.generate_assets()

    @api.onchange('asset_category_id')
    def _onchange_asset_category_id(self):
        if self.move_id.type == 'out_invoice' and self.asset_category_id:
            self.account_id = self.asset_category_id.asset_account_id.id
        elif self.move_id.type == 'in_invoice' and self.asset_category_id:
            if self.product_id.type == 'product':
                self.account_id = self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id
            else:
                self.account_id = self.asset_category_id.asset_account_id.id

    @api.onchange('product_uom_id')
    def _onchange_uom_id(self):
        result = super(AccountMoveLine, self)._onchange_uom_id()
        self._onchange_asset_category_id()
        return result

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        for r in self:
            if r.product_id:
                if r.move_id.type == 'out_invoice':
                    r.asset_category_id = r.product_id.product_tmpl_id.deferred_revenue_category_id
                elif r.move_id.type == 'in_invoice':
                    r.asset_category_id = r.product_id.product_tmpl_id.asset_category_id
        return res

    def _set_additional_fields(self, invoice):
        if not self.asset_category_id:
            if invoice.type == 'out_invoice':
                self.asset_category_id = self.product_id.product_tmpl_id.deferred_revenue_category_id.id
            elif invoice.type == 'in_invoice':
                self.asset_category_id = self.product_id.product_tmpl_id.asset_category_id.id
            self._onchange_asset_category_id()
        super(AccountMoveLine, self)._set_additional_fields(invoice)

    def _copy_data_extend_business_fields(self, values):
        super(AccountMoveLine, self)._copy_data_extend_business_fields(values)
        # we don't want asset_category_id in refund
        values['asset_category_id'] = False
