from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    amount_double_validation = fields.Monetary(string='Employee Advance Double Validation', default=0.0,
                        help="If the mount is greater than zero, any employee advance request"
                        " for the amount that is greater than or equal to this will require double validation")

    @api.constrains('amount_double_validation')
    def _check_amount_double_validation_positive(self):
        for r in self:
            if r.currency_id.compare_amounts(r.amount_double_validation, 0.0) == -1:
                raise ValidationError(_("Employee Advance Double Validation must be greater than or equal to zero."))

    def _prepare_employee_advance_journal_data(self):
        self.ensure_one()
        return {
            'name': _('Employee Advance Journal'),
            'code': 'EAJ',
            'type': 'general',
            'is_advance_journal': True,
            'company_id': self.id,
            'sequence': 99,
            'show_on_dashboard': False,
        }

    def _generate_employee_advance_account_journals(self):
        """
        To be called by post_init_hook
        """
        AccountJournal = self.env['account.journal'].sudo()
        vals_list = []
        for company in self.search([('chart_template_id', '!=', False)]):
            jounal = AccountJournal.search([('code', '=', 'EAJ'), ('is_advance_journal', '=', True), ('company_id', '=', company.id)])
            if not jounal:
                vals_list.append(company._prepare_employee_advance_journal_data())
        if vals_list:
            AccountJournal.create(vals_list)
