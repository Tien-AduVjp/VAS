from odoo import api, fields, models


class AssignToInvoiceWizard(models.TransientModel):
    _name = 'add.so.to.payment.wizard'
    _description = 'Add Sales Orders To Payment Wizard'

    account_payment_id = fields.Many2one('account.payment', string='Account Payment', required=True)
    sale_order_ids = fields.Many2many('sale.order', string='Sales Orders',
                          required=True,
                          domain="[('partner_id', '=', current_partner_id), \
                                  ('id', 'not in', current_sale_order_ids), ('state', 'not in', ['draft','sent'])]",
                          help="The sales orders that is added to this payment")
    current_sale_order_ids = fields.Many2many('sale.order', string='Payment Related Sales Orders', related='account_payment_id.sale_order_ids',
                          help="The sales orders on this payment to filter")
    current_partner_id = fields.Many2one('res.partner', related='account_payment_id.partner_id',
                                         string='Partner', help="Technical field to filter")

    @api.model
    def default_get(self, fields_list):
        res = super(AssignToInvoiceWizard, self).default_get(fields_list)
        if 'account_payment_id' not in res:
            res['account_payment_id'] = self.env['account.payment'].browse(self._context.get('active_id', False)).id
        return res

    def add(self):
        self.ensure_one()
        self.account_payment_id.write({'sale_order_ids': [(4, so.id) for so in self.sale_order_ids]})
        return True
