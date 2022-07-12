from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    advance_payment_amount = fields.Monetary("Advance Payment Amount", compute='_compute_advance_payment_amount', groups='account.group_account_invoice')
    advance_payment_ids = fields.Many2many('account.payment', string="Advance Payments", groups='account.group_account_invoice', copy=False)

    @api.depends('advance_payment_ids.amount', 'advance_payment_ids.currency_id', 'advance_payment_ids.state')
    def _compute_advance_payment_amount(self):
        for r in self:
            r.advance_payment_amount = r.advance_payment_ids._calculate_advance_payment_amount_with_po(r.currency_id)

    def action_view_advance_payment(self):
        advance_payments = self.mapped('advance_payment_ids')
        action = {
            'name': 'Advance Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', advance_payments.ids)],
            'target': 'current',
        }
        if len(advance_payments) == 1:
            action['res_id'] = advance_payments.id
            action['view_mode'] = 'form'
        return action
