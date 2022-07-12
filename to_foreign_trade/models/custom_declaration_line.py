from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CustomDeclarationLine(models.Model):
    _name = 'custom.declaration.line'
    _description = 'Custom Clearance Request Line'

    custom_declaration_import_id = fields.Many2one('custom.declaration.import', string="Custom Clearance Request (Import)", ondelete='cascade')
    custom_declaration_export_id = fields.Many2one('custom.declaration.export', string="Custom Clearance Request (Export)", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product", required=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', compute='_compute_company', store=True)
    qty = fields.Float(string="Quantity", required=True, readonly=True)
    product_uom = fields.Many2one('uom.uom', string='UoM', compute='_compute_product_uom', store=True, help="The unit of measure on the original order.")
    price_unit = fields.Monetary(string='Unit Price', compute='_compute_prices', help='The unit price at order',
                                 currency_field='currency_id')
    price_total = fields.Monetary(string='Total Price', compute='_compute_prices', help='The total price at order',
                                  currency_field='currency_id')
    total_cost = fields.Monetary(string='Taxable Value', compute='_compute_total_costs', currency_field='company_currency_id', store=True,
                                 help="The total cost of the line in company's currency. It is calculated based on either stock value for the importing goods"
                                 " or sale price for exporting goods")
    total_cost_currency = fields.Monetary(string='Currency Taxable Value',
                                         currency_field='currency_id', store=True)
    stock_move_id = fields.Many2one('stock.move', string='Stock Move')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    currency_id = fields.Many2one('res.currency', string='Currency on Order', compute='_compute_currency', store=True)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,
        help='Utility field to express amount currency', store=True)
    currency_rate = fields.Float(string='Currency Rate', compute='_compute_currency_rate', store=True, digits='Account')

    tax_ids = fields.Many2many('account.tax', 'custom_declaration_line_tax_rel', 'custom_declaration_line_id', 'account_tax_id', string='Taxes')

    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    @api.constrains('custom_declaration_import_id', 'custom_declaration_export_id')
    def _constrains_import_export(self):
        for r in self:
            if r.custom_declaration_import_id and r.custom_declaration_export_id:
                raise ValidationError(_('You cannot have a custom declaration report line that belongs/links'
                                        ' to both Export Custom Declaration and Import Custom Declaration'))
            elif not r.custom_declaration_import_id and not r.custom_declaration_export_id:
                raise ValidationError(_("No custom declaration is defined for the custom declaration line."))

    @api.depends('custom_declaration_import_id.company_id', 'custom_declaration_export_id.company_id')
    def _compute_company(self):
        for r in self:
            if r.custom_declaration_import_id:
                r.company_id = r.custom_declaration_import_id.company_id
            elif r.custom_declaration_export_id:
                r.company_id = r.custom_declaration_export_id.company_id
            else:
                r.company_id = False

    @api.depends('custom_declaration_import_id.currency_id', 'custom_declaration_export_id.currency_id')
    def _compute_currency(self):
        for r in self:
            if r.custom_declaration_import_id:
                r.currency_id = r.custom_declaration_import_id.currency_id
            elif r.custom_declaration_export_id:
                r.currency_id = r.custom_declaration_export_id.currency_id
            else:
                r.currency_id = False

    @api.depends('custom_declaration_import_id.currency_rate', 'custom_declaration_export_id.currency_rate')
    def _compute_currency_rate(self):
        for r in self:
            if r.custom_declaration_import_id:
                r.currency_rate = r.custom_declaration_import_id.currency_rate
            elif r.custom_declaration_export_id:
                r.currency_rate = r.custom_declaration_export_id.currency_rate
            else:
                r.currency_rate = 1.0

    @api.depends('custom_declaration_import_id', 'custom_declaration_export_id', 'stock_move_id.purchase_line_id.product_uom', 'sale_order_line_id.product_uom')
    def _compute_product_uom(self):
        for r in self:
            if r.custom_declaration_import_id:
                r.product_uom = r.stock_move_id.purchase_line_id.product_uom
            elif r.custom_declaration_export_id:
                r.product_uom = r.sale_order_line_id.product_uom
            else:
                r.product_uom = False

    @api.depends('custom_declaration_import_id', 'stock_move_id.purchase_line_id.price_unit', 'stock_move_id.purchase_line_id.price_total',
                 'custom_declaration_export_id', 'sale_order_line_id.price_unit', 'sale_order_line_id.price_total')
    def _compute_prices(self):
        for r in self:
            if r.custom_declaration_import_id:
                r.price_unit = r.stock_move_id.purchase_line_id.price_unit
                r.price_total = r.stock_move_id.purchase_line_id.price_total
            elif r.custom_declaration_export_id:
                r.price_unit = r.sale_order_line_id.price_unit
                r.price_total = r.sale_order_line_id.price_total

    @api.depends('currency_id', 'currency_rate', 'total_cost_currency')
    def _compute_total_costs(self):
        for r in self:
            r.total_cost = r.currency_rate * r.total_cost_currency

    @api.model_create_multi
    def create(self, vals):
        res = super(CustomDeclarationLine, self).create(vals)
        return res
       
    def write(self, vals):
        res = super(CustomDeclarationLine, self).write(vals)
        return res
    
    def _prepare_tax_line_vals(self, tax):
        if not tax['account_id']:
            raise ValidationError(_("Could not find an account for the tax '%s'. Please open the tax and specify an account for it") % tax['name'])
        vals = {
            'product_id': self.product_id.id,
            'qty': self.qty,
            'name': tax['name'],
            'tax_id': isinstance(tax['id'], models.NewId) and tax['id'].origin or tax['id'],
            'tax_repartition_line_id': isinstance(tax['tax_repartition_line_id'], models.NewId) \
                        and tax['tax_repartition_line_id'].origin or tax['tax_repartition_line_id'],
            'currency_amount_tax': tax['amount'],
            'base': tax['base'],
            'manual': False,
            'sequence': tax['sequence'],
            'account_id': tax['account_id'] or tax['refund_account_id'],
            'custom_declaration_line_id': isinstance(self.id, models.NewId) and self._origin.id or self.id,
        }
        if self.custom_declaration_import_id:
            vals['custom_declaration_id'] = self.custom_declaration_import_id.id
            vals['payment_term_id'] = self.custom_declaration_import_id.company_id.import_tax_payment_term
        if self.custom_declaration_export_id:
            vals['custom_declaration_id'] = self.custom_declaration_export_id.id
            vals['payment_term_id'] = self.custom_declaration_export_id.company_id.export_tax_payment_term
        # If the taxes generate moves on the same financial account as the invoice line,
        # propagate the analytic account from the invoice line to the tax line.
        # This is necessary in situations were (part of) the taxes cannot be reclaimed,
        # to ensure the tax move is allocated to the proper analytic account.
        if not vals.get('account_analytic_id') and self.account_analytic_id and vals['account_id'] in self.mapped('tax_ids.invoice_repartition_line_ids.account_id').ids:
            vals['account_analytic_id'] = self.account_analytic_id.id

        return vals

    def get_taxes_values(self):
        tax_list = []
        for line in self:
            partner_id = line.custom_declaration_import_id.partner_id if line.custom_declaration_import_id else line.custom_declaration_export_id.partner_id
            taxes = line.tax_ids.compute_all(price_unit=line.total_cost, currency=line.company_currency_id, product=line.product_id, partner=partner_id, is_refund = True if line.custom_declaration_export_id else False, handle_price_include=True)['taxes']
            for tax in taxes:
                val = line._prepare_tax_line_vals(tax)
                tax_list.append(val)
        return tax_list
