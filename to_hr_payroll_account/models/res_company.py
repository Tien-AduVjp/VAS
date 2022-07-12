from odoo import models, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    payslip_batch_journal_entry = fields.Boolean(string="Payslip Batch Journal Entry", default=False,
                                               help="If enabled, a single journal entry will be generated for all payslips of a payslip batch."
                                               " Otherwise, each payslip will generate a journal entry.")

    def _prepare_salary_journal_data(self):
        return {
            'name': _('Employee Salary'),
            'type': 'general',
            'code': 'SAL',
            'company_id':self.id,
            }

    def _generate_salary_account_journals(self):
        """
        To be called by post_init_hook
        """
        AccountJournal = self.env['account.journal']
        vals_list = []
        for company in self.search([('chart_template_id', '!=', False)]):
            jounal = AccountJournal.search([('code', '=', 'SAL'), ('company_id', '=', company.id)])
            if not jounal:
                vals_list.append(company._prepare_salary_journal_data())
        if vals_list:
            self.env['account.journal'].sudo().create(vals_list)

    def _fill_journal_to_payslips(self):
        """
        To be called by post_init_hook
        """
        for company in self.search([('chart_template_id', '!=', False)]):
            journal = self.env['account.journal'].search([('code', '=', 'SAL'), ('company_id', '=', company.id)], limit=1)
            if not journal:
                continue
            self.env['hr.contract'].search([('company_id', '=', company.id)]).sudo().write({
                'journal_id': journal.id
                })
            self.env['hr.payslip.run'].search([('company_id', '=', company.id)]).sudo().write({
                'journal_id': journal.id
                })
            self.env['hr.payslip'].search([('company_id', '=', company.id)]).sudo().write({
                'journal_id': journal.id
                })

    def _prepare_payslip_batch_data(self, start_date, end_date):
        self.ensure_one()
        vals = super(ResCompany, self)._prepare_payslip_batch_data(start_date, end_date)
        vals['journal_id'] = self.env['hr.payslip.run']._get_default_journal_id().id
        return vals
