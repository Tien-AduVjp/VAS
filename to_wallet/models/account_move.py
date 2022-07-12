from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    wallet_total = fields.Monetary(string='Wallet Total', compute='_compute_wallet_total', store=True,
                                   readonly=False, states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]},
                                   help="The total amount of wallet invoice lines")

    @api.depends('invoice_line_ids', 'invoice_line_ids.price_total', 'invoice_line_ids.wallet')
    def _compute_wallet_total(self):
        wallet_lines = self.mapped('invoice_line_ids').filtered(lambda l: l.wallet)
        for r in self:
            r.wallet_total = sum(wallet_lines.filtered(lambda l: l.move_id == r).mapped('price_total'))

    def _get_receivable_wallet_lines(self):
        """
        This method get all the receivable move lines of the invoices in self that are wallet operations related
        """
        return self.mapped('line_ids').filtered(lambda l: l.account_id.internal_type == 'receivable' and l.wallet)

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        self.filtered(lambda m: m.move_type in ('out_invoice', 'out_refund', 'entry')).mapped('line_ids')._update_wallet_amount()
        return res
