from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    amount_double_validation = fields.Monetary(string="Employee Advance Double Validation", default=0.0,
                        help="If the mount is greater than zero, any employee advance request"
                        " for the amount that is greater than or equal to this will require double validation")
    use_employee_advance_pass_through_account = fields.Boolean(string='Use Pass-Through Account In Employee Advance')

    @api.constrains('use_employee_advance_pass_through_account')
    def _check_use_employee_advance_pass_through_account(self):
        employee_advances = self.env['employee.advance'].sudo().search([('state', '=', 'validate')])
        if employee_advances:
            for r in self:
                emds_pass_through_account = employee_advances.filtered(lambda e: e.company_id == r and e.move_id)
                emds_dont_pass_through_account = employee_advances.filtered(lambda e: e.company_id == r) - emds_pass_through_account
                if r.use_employee_advance_pass_through_account:
                    if not emds_dont_pass_through_account:
                        continue
                else:
                    if not emds_pass_through_account:
                        continue
                raise ValidationError(_("There are still some employee advances (as listed below) being in progress."
                                        " Please get them done or cancelled before you could be able to change \"Use"
                                        " Pass-Through Account In Employee Advance\".\n%s")
                                        % (',').join((emds_pass_through_account + emds_dont_pass_through_account).mapped('name')))

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
            'type': 'general', # set type = 'general' to not create account by Odoo which type has cash or bank. After creating a journal, we will update it to 'cash'
            'company_id': self.id,
            'is_advance_journal': True,
            'show_on_dashboard': False,
            }

    def _update_employee_advance_journal_if_exists(self):
        """ This function to find advance journals and update thier type to 'cash'. Because they has created with type is 'general' before. 
        """
        self.ensure_one()
        Journal = self.env['account.journal'].sudo()
        journals = Journal.search([('code', '=', 'EAJ'), ('is_advance_journal', '=', True), ('company_id', '=', self.id)])
        if not journals:
            journals = Journal.search([('code', '=', 'EAJ'), ('company_id', '=', self.id)])
            if journals:
                return journals.write({'is_advance_journal': True, 'type': 'cash'})
            return False
        else:
            return journals.write({'type': 'cash'})
        
    def create_employee_advance_journal_if_not_exists(self):
        Journal = self.env['account.journal'].sudo()
        vals_list = []
        for r in self:
            if not r._update_employee_advance_journal_if_exists():
                vals_list.append(r._prepare_employee_advance_journal_data())
        
        if vals_list:        
            journals = Journal.create(vals_list)
            journals.write({'type': 'cash'})
