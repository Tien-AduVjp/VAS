from odoo import fields, models, _
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_account_bank_cash = fields.Boolean('Bank & Cash Moves')
    kpi_account_bank_cash_value = fields.Monetary(compute='_compute_kpi_account_bank_cash_value')

    def _compute_kpi_account_bank_cash_value(self):
        if not self.env.user.has_group('account.group_account_user'):
            raise AccessError(_("Access denied for non account user, ignore bank and cash data for digest email"))
        AccountMove = self.env['account.move']
        for r in self:
            domain = self._prepare_bank_cash_kpi_domain()
            account_moves = AccountMove.read_group(domain, ['journal_id', 'amount_total'], ['journal_id'])
            r.kpi_account_bank_cash_value = sum([account_move['amount_total'] for account_move in account_moves])
    
    def _prepare_bank_cash_kpi_domain(self):
        """
        Hook method to prepare bank & cash kpi account domain
        """
        start_date, end_date, company = self._get_kpi_compute_parameters()
        domain = [
            ('journal_id.type', 'in', ['cash', 'bank']),
            ('date', '>=', start_date),
            ('date', '<', end_date),
            ('company_id', '=', company.id)]
        return domain

    def compute_kpis_actions(self, company, user):
        res = super(Digest, self).compute_kpis_actions(company, user)
        res['kpi_account_bank_cash'] = 'account.open_account_journal_dashboard_kanban&menu_id=%s' % str(self.env.ref('account.menu_finance').id)
        return res
