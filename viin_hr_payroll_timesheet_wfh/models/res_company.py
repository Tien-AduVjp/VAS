# -*- coding: utf-8 -*-
from odoo import models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_pow_timesheet_salary_rule_vals(self, struct):
        self.ensure_one()
        return {
            'name': _('Missing PoW Timesheet'),
            'sequence': 181,
            'code': 'POWTIMESHEET',
            'struct_id': struct.id,
            'category_id': self._get_salary_rule_categ('TIMESHEET').id,
            'condition_select': 'python',
            'condition_python': """result = True if hasattr(employee, 'pow_timesheet_required') and employee.pow_timesheet_required else False""",
            'amount_select': 'code',
            'appears_on_payslip': True,
            'amount_python_compute': """
result = -1 * payslip.missing_pow_hours * employee.timesheet_cost

""",
            'register_id': self._get_contribution_register(_("HR Timesheet")).id,
            'company_id': self.id
            }

    def _prepare_pow_timesheet_salary_rule_vals_if_not_exist(self, struct):
        self.ensure_one()
        vals = self._prepare_pow_timesheet_salary_rule_vals(struct)
        existing_rules = self.env['hr.salary.rule'].sudo().search([
            ('struct_id', '=', struct.id),
            ('company_id', '=', self.id),
            ('code', '=', vals['code'])
            ])
        return vals if not existing_rules else {}

    def _generate_pow_timesheet_salary_rules(self):
        structs = self.env['hr.payroll.structure'].sudo().search([
            ('company_id', 'in', self.ids),
            ('code', '=', 'BASE')
            ])
        vals_list = []
        for r in self:
            for struct in structs.filtered(lambda sal_struct: sal_struct.company_id.id == r.id):
                rule_data = r._prepare_pow_timesheet_salary_rule_vals_if_not_exist(struct)
                if bool(rule_data):
                    vals_list.append(rule_data)
        return self.env['hr.salary.rule'].sudo().create(vals_list)

    def _parepare_salary_rules_vals_list(self, struct):
        """
        Override to have PoW Timesheet rules generated from newly created companies
        """
        self.ensure_one()
        res = super(ResCompany, self)._parepare_salary_rules_vals_list(struct)
        res.append(self._prepare_pow_timesheet_salary_rule_vals(struct))
        return res
