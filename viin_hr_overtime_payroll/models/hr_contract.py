from odoo import api, models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    overtime_base_mode = fields.Selection(selection_add=[
        ('gross', 'Gross Salary'),
        ('wage_and_advantages', 'Wage Plus Configurable Advantages')], default='gross',
        help="The overtime base mode for overtime pay computation.\n"
        "* Manual Input: you can define any base amount below manually;\n"
        "* Basic Wage: the base amount will be the contract's basic wage;\n"
        "* Gross Salary: the base amount will be the contract's Gross Salary;\n"
        "* Wage Plus Configurable Advantages: the base amount will be the contract's Wage"
        " plus the contract's advantages whose templates having Overtime Base Factor enabled;\n")

    @api.depends('advantage_ids', 'advantage_ids.amount', 'gross_salary')
    def _compute_overtime_base_amount(self):
        super(HrContract, self)._compute_overtime_base_amount()

    def _get_overtime_base_amount(self):
        if self.overtime_base_mode == 'wage':
            ot_base = self.wage
        elif self.overtime_base_mode == 'gross':
            ot_base = self.gross_salary
        elif self.overtime_base_mode == 'wage_and_advantages':
            ot_base = self.wage + sum(self.advantage_ids.filtered(lambda adv: adv.overtime_base_factor).mapped('amount'))
        else:
            ot_base = self.gross_salary
        return ot_base

    def _get_month_cycle_start_end(self, date_start=None, date_end=None):
        now = fields.Datetime.now()
        date_start = date_start or now
        date_end = date_end or now
        salary_cycle = self.company_id.salary_cycle_id or self.env.ref('to_hr_payroll.hr_salary_cycle_default', raise_if_not_found=False)
        if not salary_cycle:
            return super(HrContract, self)._get_month_cycle_start_end(date_start, date_end)
        else:
            return salary_cycle._get_month_start_date(date_start), salary_cycle._get_month_end_date(date_end)
    
