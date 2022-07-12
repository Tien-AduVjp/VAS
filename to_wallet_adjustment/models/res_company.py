from odoo import models, fields, _

WALLET_ADJUSTMENT_JOURNAL_CODE = 'WLA'


class ResCompany(models.Model):
    _inherit = 'res.company'

    wallet_adjustment_journal_id = fields.Many2one('account.journal', compute='_compute_wallet_adjustment_journal_id')

    def _compute_wallet_adjustment_journal_id(self):
        journals = self.env['account.journal'].search([
            ('company_id', 'in', self.ids),
            ('code', '=', WALLET_ADJUSTMENT_JOURNAL_CODE)
        ])
        for r in self:
            r.wallet_adjustment_journal_id = journals.filtered(lambda j: j.company_id == r)[:1]

    def _prepare_wallet_adjustment_journal_values(self):
        self.ensure_one()
        return {
            'name': _('Wallet Adjustments'),
            'type': 'general',
            'code': WALLET_ADJUSTMENT_JOURNAL_CODE,
            'company_id': self.id
        }

    def _create_wallet_adjustment_journal_if_not_exist(self):
        journals = self.env['account.journal']
        for r in self:
            if r.chart_template_id and not r.wallet_adjustment_journal_id:
                vals = r._prepare_wallet_adjustment_journal_values()
                journal = journals.create(vals)
                journals += journal
        return journals

    def _install_wallet_adjustment_journals(self):
        """
        To be called by post_init_hook only to generate journal for existing companies that having chart of accounts installed.
        """
        return self.search([('chart_template_id','!=', False)])._create_wallet_adjustment_journal_if_not_exist()
