from odoo import models, fields


class WalletAdjust(models.TransientModel):
    _name = 'wallet.adjust'
    _description = "Wallet Adjustment Wizard"

    amount = fields.Float(required=True, help='A positive or negative value to add to wallet')
    journal_id = fields.Many2one('account.journal', required=True,
                                 default=lambda self: self.env.company.wallet_adjustment_journal_id)
    wallet_id = fields.Many2one('wallet', required=True, default=lambda self: self.env.context.get('active_id'))
    date = fields.Date(string='Force Adjustment Date', help="If specified, the corresponding journal entry will use this date instead of the current date.")

    def action_adjust(self):
        wallet = self.wallet_id
        if self.date:
            wallet = wallet.with_context(force_period_date=self.date)
        move = wallet._adjust(self.amount, self.journal_id)
        action = self.env.ref('account.action_move_journal_line').read()[0]
        # override the context to get rid of the default filtering
        action['context'] = {}
        action['domain'] = [('id', 'in', move.ids)]
        return action
