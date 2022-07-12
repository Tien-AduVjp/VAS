from odoo import fields, models, api


class AccountPaymentLine(models.Model):
    _name = 'account.payment.line'
    _description = 'Payment Line'

    name = fields.Char(string='Label', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    account_id = fields.Many2one('account.account', string='Countered Account', required=True,
                                 domain="[('deprecated','=',False),('reconcile','=',True)]",
                                 compute='_compute_account_id', readonly=False, store=True,
                                 help="The account that is countered with the corresponding payment's bank/cash account.")
    payment_id = fields.Many2one('account.payment', string='Payment', required=True, ondelete='cascade', readonly=True)
    currency_id = fields.Many2one(related='payment_id.currency_id')
    amount = fields.Monetary(string='Amount', required=True)
    move_line_ids = fields.Many2many('account.move.line', string='Move Lines')
    amount_suggested = fields.Monetary(string='Amount Suggested')

    @api.depends('payment_id')
    def _compute_account_id(self):
        for r in self:
            r.account_id = r.payment_id.destination_account_id or False
