from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    advance_payment_amount = fields.Monetary(string='Reconciled Payments Amount', compute='_compute_advance_payment_amount', groups='account.group_account_invoice')
    advance_payment_ids = fields.Many2many('account.payment', string='Advance Payments', groups='account.group_account_invoice', copy=False)
    advance_payment_count = fields.Integer(string='Payments Count', compute='_compute_advance_payment_count', groups='account.group_account_invoice')

    def _compute_advance_payment_count(self):
        for r in self:
            r.advance_payment_count = len(r.advance_payment_ids)

    @api.depends('invoice_ids.line_ids', 'advance_payment_ids.amount', 'advance_payment_ids.currency_id', 'advance_payment_ids.state')
    def _compute_advance_payment_amount(self):
        for r in self:
            invoice_partials = []
            for i in r.invoice_ids:
                invoice_partials.extend(i._get_reconciled_invoices_partials())

            if invoice_partials:
                r.advance_payment_amount = sum(i[1] for i in invoice_partials)
            else:
                r.advance_payment_amount = 0

    def action_open_reconcile_view(self):
        return self.invoice_ids.open_reconcile_view()

    def action_view_advance_payment(self):
        advance_payments = self.mapped('advance_payment_ids')
        action = {
            'name': _('Payments'),
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
