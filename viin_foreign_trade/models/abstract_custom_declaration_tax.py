import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class CustomDeclarationTax(models.AbstractModel):
    _name = "abstract.custom.declaration.tax"
    _order = 'sequence, product_id, id'
    _description = "Custom Declaration Tax"

    name = fields.Char(string='Tax Description', required=True)
    tax_id = fields.Many2one('account.tax', string='Tax', ondelete='restrict')
    tax_repartition_line_id = fields.Many2one('account.tax.repartition.line',
                                              string="Originator Tax Repartition Line", ondelete='restrict', readonly=True,
                                              help="Tax repartition line that caused the creation of this move line, if any")
    is_vat = fields.Boolean(string='Is VAT', related='tax_id.is_vat', store=True, index=True, readonly=True)
    account_id = fields.Many2one('account.account', string='Tax Account', required=True, domain=[('deprecated', '=', False)])
    amount = fields.Monetary(string="Tax Amount", compute='_compute_amount_tax', store=True, currency_field='company_currency_id',
                             readonly=False)
    currency_amount_tax = fields.Monetary(string='Amount (in Order Currency)',
                                          compute='_compute_currency_amount_tax', currency_field='currency_id',
                                          store=True)
    manual = fields.Boolean(default=True)
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of custom declaration tax.")
    company_id = fields.Many2one('res.company', string='Company', compute='_compute_currency', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=True, compute='_compute_currency')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Company Currency', readonly=True,
        help='Utility field to express amount currency', store=True)
    currency_rate = fields.Float(string='Currency Rate', compute='_compute_currency', store=True)
    base = fields.Monetary(string='Base', compute='_compute_base_amount')

    product_id = fields.Many2one('product.product', string="Product", required=True, readonly=True)
    qty = fields.Float(string="Quantity")
    payment_term_id = fields.Many2one('account.payment.term', string="Tax Payment Term")
    partner_id = fields.Many2one('res.partner', string='Partner')
#     balance = fields.Monetary(string="Balance", compute='_get_balance', currency_field='company_currency_id', store=True)
    move_id = fields.Many2one('account.move', string='Account Move')
    paid = fields.Boolean(string='Paid', default=False)
    custom_declaration_line_id = fields.Many2one('custom.declaration.line', string='Custom Declaration Line', readonly=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    stock_move_id = fields.Many2one('stock.move', string='Stock Move')

    @api.onchange('partner_id')
    def _onchangge_partner_id(self):
        if self.partner_id and self.partner_id.property_supplier_payment_term_id:
            self.payment_term_id = self.partner_id.property_supplier_payment_term_id

    @api.depends('currency_rate', 'currency_amount_tax')
    def _compute_amount_tax(self):
        raise ValidationError(_("The method _compute_amount_tax() has not been implemented for the model '%s'"), self._name)

    @api.depends('currency_rate')
    def _compute_currency_amount_tax(self):
        for r in self:
            try:
                r.currency_amount_tax = r.amount / r.currency_rate
            except ZeroDivisionError:
                raise ValidationError(_("Currency Rate cannot be zero!"))

    def _compute_base_amount(self):
        for r in self:
            base = 0.0
            taxes = r.custom_declaration_id.custom_declaration_line_ids.get_taxes_values()
            for tax in taxes:
                if tax['product_id'] == r.product_id.id and tax['tax_id'] == r.tax_id.id and tax['stock_move_id'] == r.stock_move_id.id:
                        base = tax['base']
            if base:
                r.base = base
            else:
                _logger.warning('Tax Base Amount not computable probably due to a change in an underlying tax (%s).', r.tax_id.name)

    def name_get(self):
        res = []
        for rec in self:
            name = '%s / %s' % (rec.product_id.name, rec.name)
            res.append((rec.id, name))
        return res

    def _prepare_declaration_tax_group_data(self):
        return {
            'custom_declaration_id': self[0].custom_declaration_id.id,
            'company_currency_id': self[0].company_currency_id.id,
            'tax_group_id': self[0].tax_id.tax_group_id.id,
            'custom_declaration_tax_line_ids': [(6, 0, self.ids)],
            }

    def _prepare_declaration_tax_group_data_list(self):
        vals_list = []
        for custom_declaration_id in self.mapped('custom_declaration_id'):
            tax_lines = self.filtered(lambda t: t.custom_declaration_id == custom_declaration_id)
            tax_group_ids = tax_lines.mapped('tax_id.tax_group_id')
            for tax_group_id in tax_group_ids:
                lines = tax_lines.filtered(lambda tl: tl.tax_id.tax_group_id == tax_group_id)
                vals_list.append(lines._prepare_declaration_tax_group_data())
        return vals_list

    def _get_custom_dec_tax_group_model(self):
        raise NotImplementedError

    def generate_custom_declaration_tax_groups(self):
        for r in self:
            if r.custom_dec_tax_group_id:
                raise ValidationError(_("Could not generate custom declaration tax group when the corresponding custom"
                                        " declaration tax line has a group already."))
        vals_list = self._prepare_declaration_tax_group_data_list()
        return self.env[self._get_custom_dec_tax_group_model()].create(vals_list)

    def ensure_allow_reconciliation(self):
        self.ensure_one()
        if self.account_id and not self.account_id.reconcile:
            raise ValidationError(_("You must set Allow Reconciliation for the account `%s` (%s) before you can proceed.")
                                  % (self.account_id.code, self.account_id.name))
        return self

    def _prepare_landed_cost_line_data(self, landed_cost):
        self.ensure_one()
        import_tax_cost_product = self.env.ref('viin_foreign_trade.to_product_product_import_tax_cost')
        accounts_data = import_tax_cost_product.product_tmpl_id.sudo().get_product_accounts()
        account = accounts_data['stock_input']
        return {
                'product_id': import_tax_cost_product.id,
                'name': self.name + ': ' + self.product_id.name,
                'split_method': 'by_quantity',
                'price_unit': self.amount,
                'cost_id': landed_cost.id,
                'account_id': account.id
            }

    def _prepare_landed_cost_adjustment_line_data(self, landed_cost_line):
        self.ensure_one()
        move = self.custom_declaration_line_id.stock_move_id
        vals = {
                'product_id': self.product_id.id,
                'name': self.name + ': ' + self.product_id.name,
                'quantity': self.qty,
                'additional_landed_cost': self.amount,
                'cost_id': landed_cost_line.cost_id.id,
                'cost_line_id': landed_cost_line.id,
                'weight': 0,
                'volume': 0,
            }
        if move:
            vals.update({
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': sum(move.stock_valuation_layer_ids.mapped('value')),
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty,
                })
        return vals
