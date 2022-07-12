from odoo import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _apply_vietnam_empoloyee_payable_account(self):
        for company in self.company_id._filter_vietnam_coa():
            employee_payable_account = company.general_employee_payable_account_id
            if not employee_payable_account:
                continue
            employees = self.sudo().filtered(lambda e: e.company_id == company and e.address_home_id)
            if employees:
                employees.address_home_id.sudo().with_company(company).write({
                        'property_account_payable_id': employee_payable_account.id
                    })

    @api.model_create_multi
    def create(self, vals_list):
        employees = super(HrEmployee, self).create(vals_list)
        employees._apply_vietnam_empoloyee_payable_account()
        return employees

    def write(self, vals):
        apply_vietnam_acc = 'address_home_id' in vals
        res = super(HrEmployee, self).write(vals)
        if apply_vietnam_acc:
            self._apply_vietnam_empoloyee_payable_account()
        return res
