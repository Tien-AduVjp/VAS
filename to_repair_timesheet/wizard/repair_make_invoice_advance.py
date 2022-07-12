from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RepairAdvancePaymentInv(models.TransientModel):
    _name = "repair.advance.payment.inv"
    _description = "Repair Advance Payment Invoice"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    @api.model
    def _get_advance_payment_method(self):
        if self._count() == 1:
            repair_obj = self.env['repair.order']
            order = repair_obj.browse(self._context.get('active_ids'))[0]
            if all([line.product_id.invoice_policy == 'order' for line in order.fees_lines]) or order.invoice_count:
                return 'all'
        return 'delivered'

    @api.model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        return self.env['product.product'].browse(int(product_id))

    @api.model
    def _default_deposit_account_id(self):
        return self._default_product_id().property_account_income_id

    @api.model
    def _default_deposit_taxes_id(self):
        return self._default_product_id().taxes_id

    advance_payment_method = fields.Selection([
        ('delivered', 'Invoiceable lines'),
        ('all', 'Invoiceable lines (deduct down payments)')
        ], string='What do you want to invoice?', default=_get_advance_payment_method, required=True)
    product_id = fields.Many2one('product.product', string='Down Payment Product', domain=[('type', '=', 'service')],
        default=_default_product_id)
    count = fields.Integer(default=_count, string='# of Orders')
    amount = fields.Float('Down Payment Amount', digits='Account', help="The amount to be invoiced in advance, taxes excluded.")
    deposit_account_id = fields.Many2one("account.account", string="Income Account", domain=[('deprecated', '=', False)],
        help="Account used for deposits", default=_default_deposit_account_id)
    deposit_taxes_id = fields.Many2many("account.tax", string="Customer Taxes", help="Taxes used for deposits", default=_default_deposit_taxes_id)


    def create_invoices(self):
        repair_orders = self.env['repair.order'].browse(self._context.get('active_ids', []))
        for ro in repair_orders:
            if not ro.partner_id:
                raise UserError(_("You have to choose a customer in repair order '%s' to create an invoice!") % ro.name)
        if self.advance_payment_method == 'delivered':
            repair_orders.action_invoice_create()
        elif self.advance_payment_method == 'all':
            repair_orders.action_invoice_create(final=True)
        if self._context.get('open_invoices', False):
            return repair_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

