from odoo import models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_expense_journal_data(self):
        self.ensure_one()
        if not self.chart_template_id:
            return {}
        default_account = self.env['account.account'].sudo().search([
            ('company_id', '=', self.id),
            ('code', '=', self.chart_template_id.property_account_expense_categ_id.code)
        ], limit=1)
        return {
            'name': _('Expense Journal'),
            'code': 'EXJ',
            'type': 'purchase',
            'company_id': self.id,
            'sequence': 99,
            'show_on_dashboard': False,
            'default_account_id': default_account.id or False,
        }

    def _generate_expense_account_journals(self):
        """
        To be called by post_init_hook
        """
        AccountJournal = self.env['account.journal'].sudo()
        vals_list = []
        for company in self.search([('chart_template_id', '!=', False)]):
            jounal = AccountJournal.search([('code', '=', 'EXJ'), ('company_id', '=', company.id)])
            if not jounal:
                vals_list.append(company._prepare_expense_journal_data())
        if vals_list:
            AccountJournal.create(vals_list)
