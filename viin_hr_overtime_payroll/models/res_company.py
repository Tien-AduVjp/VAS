from odoo import models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_hr_advantage_templates(self):
        vals_list = super(ResCompany, self)._prepare_hr_advantage_templates()
        for vals in vals_list:
            vals['overtime_base_factor'] = True
        return vals_list

    def _prepare_contribution_register_data(self):
        res = super(ResCompany, self)._prepare_contribution_register_data()
        wage_categ = self.env.ref('to_hr_payroll.hr_contribution_register_wage_allowance')
        res.append({
            'name': _('Overtime'),
            'partner_id': False,
            'category_id': wage_categ.id,
            'company_id': self.id
            })
        return res

    def _prepare_salary_rule_categories_data(self):
        categ_list = super(ResCompany, self)._prepare_salary_rule_categories_data()
        for categ in categ_list:
            if categ['code'] == 'ALW':
                categ['children_ids'].append(
                    (0, 0, {'name': _('Taxed Overtime'), 'code': 'TAXED_OT', 'company_id': self.id, 'paid_by_company': True}),
                    )
            if categ['code'] == 'ALWNOTAX':
                categ['children_ids'].append(
                    (0, 0, {'name': _('Untaxed Overtime'), 'code': 'UNTAXED_OT', 'company_id': self.id, 'paid_by_company': True}),
                    )
        return categ_list

    def _prepare_overtime_salary_rules(self, struct):
        """
        # TODO 15.0: edit overtime rule with 13th payslip
        # if 13th payslip:
        #     pass
        """

        self.ensure_one()
        return [
            {
                'name': _('Taxed Overtime Work'),
                'sequence': 565,
                'code': 'TAXED_OT',
                'struct_id': struct.id,
                'category_id': self._get_salary_rule_categ('TAXED_OT').id,
                'condition_select': 'python',
                'condition_python': 'result = True if payslip.overtime_plan_line_ids else False',
                'amount_select': 'code',
                'appears_on_payslip': True,
                'amount_python_compute': """
if payslip.thirteen_month_pay:
    result = 0.0
else:
    result = sum(payslip.overtime_plan_line_ids.mapped('standard_pay'))
""",
                'register_id': self._get_contribution_register(_("Overtime")).id,
                'company_id': self.id
                },
            {
                'name': _('Untaxed Overtime Work'),
                'sequence': 4200,
                'code': 'UNTAXED_OT',
                'struct_id': struct.id,
                'category_id': self._get_salary_rule_categ('UNTAXED_OT').id,
                'condition_select': 'python',
                'condition_python': 'result = True if payslip.overtime_plan_line_ids else False',
                'amount_select': 'code',
                'appears_on_payslip': True,
                'amount_python_compute': """
if payslip.thirteen_month_pay:
    result = 0.0
else:
    total_overtime_pay = sum(payslip.overtime_plan_line_ids.mapped('actual_overtime_pay'))
    untaxed_overtime_pay = sum(payslip.overtime_plan_line_ids.mapped('standard_pay'))
    result = total_overtime_pay - untaxed_overtime_pay
""",
                'register_id': self._get_contribution_register(_("Overtime")).id,
                'company_id': self.id
                },
            ]

    def _parepare_salary_rules_vals_list(self, struct):
        res = super(ResCompany, self)._parepare_salary_rules_vals_list(struct)
        res += self._prepare_overtime_salary_rules(struct)
        return res
