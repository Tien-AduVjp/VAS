from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    children = fields.Integer(compute='_compute_dependant', store=True, groups='hr.group_hr_user')
    other_dependant = fields.Integer(string='Other Dependant', compute='_compute_dependant', store=True,
                                     tracking=True, groups="hr.group_hr_user",
                                     help="Number of other people that are dependent on this employee.")
    slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips', readonly=True)
    payslips_count = fields.Integer(compute='_compute_payslips_count', string='Payslips Count',
                                    groups="to_hr_payroll.group_hr_payroll_user")

    payroll_contribution_reg_ids = fields.One2many('hr.payroll.contribution.register', 'employee_id',
                                        domain=[('state', '!=', 'draft')],
                                        string='Payroll Contribution to 3rd-Party', readonly=True)

    payroll_contribution_reg_count = fields.Integer(compute='_compute_payroll_contribution_reg_count', string='Payroll Contribution Register')
    total_dependant = fields.Integer(string='Total Dependant', compute='_compute_dependant', store=True, tracking=True, groups="hr.group_hr_user",
                                     help="Total number of people that are dependent on this employee.")
    personal_income_tax_analysis_line_ids = fields.One2many('payslip.personal.income.tax.analysis', 'employee_id',
                                                            string='Personal Income Tax Analysis Lines')
    contract_currency_id = fields.Many2one(related='contract_id.currency_id', string='Current Contract Currency')
    gross_salary = fields.Monetary(related='contract_id.gross_salary', string='Current Gross Salary',
                                   currency_field='contract_currency_id',
                                   groups="hr_contract.group_hr_contract_manager,to_hr_payroll.group_hr_payroll_user",
                                   help="The Gross Salary of the current contract of the employee")

    @api.depends('relative_ids', 'relative_ids.is_dependant', 'relative_ids.type')
    def _compute_dependant(self):
        for r in self:
            dependant = r.relative_ids.filtered(lambda rel: rel.is_dependant)
            children_dependant = dependant.filtered(lambda dep: dep.type == 'children')
            other_dependant = dependant - children_dependant
            r.total_dependant = len(dependant)
            r.children = len(children_dependant)
            r.other_dependant = len(other_dependant)

    def _compute_payslips_count(self):
        payslip_data = self.env['hr.payslip'].read_group([('employee_id', 'in', self.ids)], ['employee_id'], ['employee_id'])
        mapped_data = dict([(dict_data['employee_id'][0], dict_data['employee_id_count']) for dict_data in payslip_data])
        for employee in self:
            employee.payslips_count = mapped_data.get(employee.id, 0)

    def _compute_payroll_contribution_reg_count(self):
        payroll_contrib_data = self.env['hr.payroll.contribution.register'].sudo().read_group([
            ('employee_id', 'in', self.ids)],
            ['employee_id'], ['employee_id']
            )
        mapped_data = dict([(it['employee_id'][0], it['employee_id_count']) for it in payroll_contrib_data])
        for r in self:
            r.payroll_contribution_reg_count = mapped_data.get(r.id, 0)

    def action_view_payroll_contribution_registers(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('to_hr_payroll.act_hr_payroll_contribution_register')
        action['context'] = {'search_default_employee_id': self.id, 'default_employee_id': self.id}
        return action

    def action_view_payslips(self):
        action = self.env['ir.actions.act_window']._for_xml_id('to_hr_payroll.act_hr_employee_payslip_list')
        # override the context to get rid of the default filtering
        action['context'] = {
            'default_employee_id': self.id,
            'default_contract_id': self.contract_id.id,
            'default_company_id': self.contract_id.company_id.id
            }

        # choose the view_mode accordingly
        if self.payslips_count != 1:
            action['domain'] = "[('employee_id', 'in', %s)]" % str(self.ids)
        elif self.payslips_count == 1:
            res = self.env.ref('to_hr_payroll.view_hr_payslip_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.slip_ids.id
        return action

    def _get_payslips_of_year(self, year):
        self.ensure_one()
        contracts = self._get_contracts_of_year(year)
        slips = self.slip_ids.filtered(
            lambda slip: \
                slip.state in ('verify', 'done') \
                and slip.contract_id in contracts \
                and slip.date_from.year == year \
                and slip.date_to.year == year
                )
        return slips.sorted_by_dates()

    def _get_last_payslip(self, include_13thmonth_pay=False):
        self.ensure_one()
        if include_13thmonth_pay:
            slips = self.slip_ids.filtered(lambda ps: ps.state in ('verify', 'done'))
        else:
            slips = self.slip_ids.filtered(lambda ps: ps.state in ('verify', 'done') and not ps.thirteen_month_pay)
        return slips.sorted_by_dates()[-1:]

    def _get_payslips(self, date_from, date_to, states=['verify', 'done']):
        """
        Returns the contracts of the employee between date_from and date_to
        """
        return self.env['hr.payslip'].search([('state', 'in', states),
                                              ('employee_id', 'in', self.ids),
                                              ('date_from', '<=', date_from),
                                              ('date_to', '>=', date_to)
                                            ])
