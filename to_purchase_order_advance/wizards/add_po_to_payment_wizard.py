from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class AssignToInvoiceWizard(models.TransientModel):
    _name = 'add.po.to.payment.wizard'
    _description = 'Add Purchases Orders To Payment Wizard'

    account_payment_id = fields.Many2one('account.payment', string='Account Payment', required=True)
    purchase_order_ids = fields.Many2many('purchase.order', string='Purchases Orders',
                          required=True,
                          domain="[('id', 'not in', current_purchase_order_ids), ('state', 'not in', ['draft', 'sent'])]",
                          help="The purchases orders that is added to this payment")
    current_purchase_order_ids = fields.Many2many('purchase.order',
                                                  related='account_payment_id.purchase_order_ids',
                                                  string='Payment Related Purchases Orders',
                          help="The purchases orders on this payment to filter")

    @api.model
    def default_get(self, fields_list):
        res = super(AssignToInvoiceWizard, self).default_get(fields_list)
        if 'account_payment_id' not in res:
            res['account_payment_id'] = self.env['account.payment'].browse(self._context.get('active_id', False)).id
        return res

    @api.onchange('account_payment_id')
    def _onchange_current_partner_id(self):
        if self.account_payment_id.partner_id:
            return {'domain': {'purchase_order_ids': [('state', 'not in', ['draft','sent']),
                                                      ('partner_id', '=', self.account_payment_id.partner_id.id),
                                                      ('id', 'not in', self.account_payment_id.purchase_order_ids.ids)]}}

    @api.onchange('purchase_order_ids')
    def _onchange_purchase_order_ids(self):
        if self.purchase_order_ids and not self.account_payment_id.partner_id:
            return {'domain': {'purchase_order_ids': [('state', 'not in', ['draft','sent']),
                                                      ('partner_id', 'in', self.purchase_order_ids.partner_id.ids)]}}

    def add(self):
        self.ensure_one()
        self.account_payment_id.write({'purchase_order_ids': [(4, so.id) for so in self.purchase_order_ids]})
        return True
