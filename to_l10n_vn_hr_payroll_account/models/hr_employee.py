from odoo import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _apply_vietnam_empoloyee_payable_account(self):
        vietnam_coa = self.env.ref('l10n_vn.vn_template')
        for company in self.mapped('company_id').filtered(lambda c: c.chart_template_id == vietnam_coa):
            employee_payable_account = self.env['account.account'].sudo().search([
                ('company_id', '=', company.id),
                ('code', '=like', '334%')
                ], limit=1)
            if not employee_payable_account:
                continue
            for r in self.sudo().filtered(lambda e: e.company_id == company and e.address_home_id):
                r.address_home_id.sudo().with_context(force_company=company.id).write({
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
