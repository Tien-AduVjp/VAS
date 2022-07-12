from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    general_overhead = fields.Float(string="General Overhead", default=1, required=True)

    def _prepare_contribution_register_data(self):
        res = super(ResCompany, self)._prepare_contribution_register_data()
        res.append({
            'name': _('HR Timesheet'),
            'partner_id': False,
            'category_id': self.env.ref('to_hr_timesheet_payroll.hr_contribution_category_timesheet').id,
            'company_id': self.id
            })
        return res

    def _prepare_salary_rule_categories_data(self):
        res = super(ResCompany, self)._prepare_salary_rule_categories_data()
        res.append({
            'name': _('HR Timesheet'),
            'code': 'TIMESHEET',
            'company_id': self.id
            })
        return res

    def _parepare_salary_rules_vals_list(self, struct):
        res = super(ResCompany, self)._parepare_salary_rules_vals_list(struct)
        res.append(self._prepare_timesheet_salary_rules(struct))
        return res

    def _prepare_timesheet_salary_rules(self, struct):
        self.ensure_one()
        return {
            'name': _('HR Timesheet Amount'),
            'sequence': 180,
            'code': 'TIMESHEET',
            'struct_id': struct.id,
            'category_id': self._get_salary_rule_categ('TIMESHEET').id,
            'condition_select': 'python',
            'condition_python': """result = True if hasattr(payslip.contract_id, 'payroll_timesheet_enabled') and payslip.contract_id.payroll_timesheet_enabled else False""",
            'amount_select': 'code',
            'appears_on_payslip': True,
            'amount_python_compute': """
result = 0.0

######### EXAMPLE #########

#### get the payslip's related timessheet log
# timesheet_lines = payslip.timesheet_line_ids

#### get the payslip's related timessheet hours
# timesheet_hours = sum(timesheet_lines.mapped('unit_amount'))

### calculate salary based on timesheet hours and contract wage
# salary = 0.0
# for line in payslip.working_month_calendar_ids:
#     period_timesheet_lines = timesheet_lines.filtered(lambda tsl: tsl.date.year == line.year_int and tsl.month == line.month_int)
#     period_timesheet_hours = sum(period_timesheet_lines.mapped('unit_amount'))
#     if period_timesheet_hours != 0.0:
#         salary += contract.wage * (line.duty_working_hours - line.unpaid_leave_hours) / period_timesheet_hours
# result = salary
""",
            'register_id': self._get_contribution_register(_("HR Timesheet")).id,
            'company_id': self.id
            }

    def _prepare_timesheet_salary_rules_data(self, struct):
        self.ensure_one()
        data = {}
        rule = self._prepare_timesheet_salary_rules(struct)
        existing_rules = self.env['hr.salary.rule'].sudo().search([('struct_id', '=', struct.id), ('company_id', '=', self.id), ('code', '=', rule['code'])])
        if not existing_rules:
            data = rule
        return data

    def _generate_timesheet_salary_rules(self):
        self._generate_contribution_register()
        self._generate_salary_rule_categories()

        salary_rule_obj = self.env['hr.salary.rule'].sudo()
        structure_obj = self.env['hr.payroll.structure'].sudo()

        for r in self:
            structs = structure_obj.search([
                ('company_id', '=', r.id),
                ('code', '=', 'BASE')
            ])

            for struct in structs:
                rule_data = r._prepare_timesheet_salary_rules_data(struct)
                if rule_data:
                    salary_rule_obj.create(rule_data)
        return True

    def _update_employee_timesheet_cost_from_payslips(self):
        """
        This method will calculate timesheet cost for all the existing timesheet records that referred by payslips
        and update the employee's timesheet cost accordingly
        """
        all_payslips = self.env['hr.payslip'].sudo().search([
            ('state', 'in', ('verify', 'done')),
            ('thirteen_month_pay', '=', False)
            ])
        all_timesheet_lines = all_payslips.sudo().timesheet_line_ids.sudo()
        for r in self:
            payslips = all_payslips.filtered(lambda ps: ps.company_id == r)
            payslip_timesheet_hour_costs = payslips._calculate_payslip_timesheet_hour_cost()

            for employee in payslips.with_context(active_test=False).mapped('employee_id'):
                # - all the timesheet that were logged before the date_to of the very first payslip of the employee
                # will be costed as that payslip cost
                # - all the timesheet that were logged after the date_from of the very last payslip of the employee
                # will be costed as that payslip cost
                # - the remaining will be costed as the corresponding payslip cost
                employee_payslips = payslips.filtered(lambda ps: ps.employee_id == employee).sorted_by_dates()
                payslips_count = len(employee_payslips)
                for idx, payslip in enumerate(employee_payslips):
                    payslip._update_employee_timesheet_cost()
                    if idx == 0:
                        timesheet_lines = all_timesheet_lines.filtered(
                            lambda l: l.date <= payslip.date_to and l.employee_id == employee and l.company_id == r)
                    elif idx < payslips_count - 1:
                        timesheet_lines = all_timesheet_lines.filtered(
                            lambda l: l.date >= payslip.date_from and l.date <= payslip.date_to and l.employee_id == employee and l.company_id == r)
                    else:
                        timesheet_lines = all_timesheet_lines.filtered(
                            lambda l: l.date >= payslip.date_from and l.employee_id == employee and l.company_id == r)

                    for line in timesheet_lines.with_context(ignore_payslip_state_check=True):
                        line.write({
                            'amount':-1 * payslip_timesheet_hour_costs.get(payslip, 0.0) * line.unit_amount
                            })
                employee_payslips._compute_timesheet_cost()
