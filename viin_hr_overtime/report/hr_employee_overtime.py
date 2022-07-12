# -*- coding: utf-8 -*-

from odoo import tools
from odoo import fields, models, api, _
from odoo.tools import format_datetime
from odoo.addons.base.models.res_partner import _tz_get

from ..models.hr_contract import OVERTIME_RECOGNITION_MODE


class EmployeeOvertime(models.Model):
    _name = 'hr.employee.overtime'
    _description = "Employee Overtime"
    _auto = False
    _rec_name = 'employee_id'
    _order = 'date_start desc'
    
    date_start = fields.Datetime(string='Start Date', readonly=True)
    date_end = fields.Datetime(string='End Date', readonly=True)
    reason_id = fields.Many2one('hr.overtime.reason', string='Reason', readonly=True)
    recognition_mode = fields.Selection(OVERTIME_RECOGNITION_MODE, string='Recognition Mode', readonly=True)
    tz = fields.Selection(_tz_get, string='Timezone', readonly=True)
    planned_hours = fields.Float(string='Planned Hours', readonly=True)
    actual_hours = fields.Float(string='Actual Hours', readonly=True)
    diff_hours = fields.Float(string='Hours Difference', readonly=True, help="The difference between the planned hours and the actual hours.")
    planned_overtime_pay = fields.Float(string='Planned Overtime Pay', readonly=True, groups="hr_contract.group_hr_contract_manager")
    actual_overtime_pay = fields.Float(string='Actual Overtime Pay', readonly=True, groups="hr_contract.group_hr_contract_manager")
    standard_pay = fields.Monetary(string='Standard Pay', readonly=True, groups="hr_contract.group_hr_contract_manager",
                                   help="The pay amount for the actual overtime hours based on the formula `Standard Pay per Hour * Actual Overtime Hours`.")
    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Schedule', readonly=True)    
    overtime_plan_id = fields.Many2one('hr.overtime.plan', string='Overtime Plan', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    hr_overtime_rule_id = fields.Many2one('hr.overtime.rule', string='Overtime Rule', readonly=True)
    rule_code_id = fields.Many2one('hr.overtime.rule.code', string='Overtime Rule Code', readonly=True)
    pay_rate = fields.Float(string='Pay Rate', readonly=True, group_operator='avg')
    global_leave_id = fields.Many2one('resource.calendar.leaves', string='Matched Global/Holiday Leave', required=True)
    job_id = fields.Many2one('hr.job', string='Job Position', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', readonly=True)
    plans_count = fields.Integer(string='Plans Count', readonly=True, group_operator='count_distinct')
    contracts_count = fields.Integer(string='Contracts Count', readonly=True, group_operator='count_distinct')
    employees_count = fields.Integer(string='Employees Count', readonly=True, group_operator='count_distinct')
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause='', where_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            row_number() OVER(ORDER BY otpl.date_start, otpl.id) AS id,
            otpl.date_start,
            otpl.date_end,
            otp.reason_id,
            otpl.recognition_mode AS recognition_mode,
            otpl.tz AS tz,
            sum(otpl.planned_hours) AS planned_hours,
            sum(otpl.actual_hours) AS actual_hours,
            sum(otpl.planned_hours-otpl.actual_hours) AS diff_hours,
            sum(otpl.planned_overtime_pay * otpl.currency_rate) AS planned_overtime_pay,
            sum(otpl.actual_overtime_pay * otpl.currency_rate) AS actual_overtime_pay,
            sum(otpl.standard_pay * otpl.currency_rate) AS standard_pay,
            cal.id AS resource_calendar_id,
            otp.id AS overtime_plan_id,
            emp.id AS employee_id,
            rul.id AS hr_overtime_rule_id,
            rulcode.id AS rule_code_id,
            otpl.pay_rate AS pay_rate,
            gleave.id AS global_leave_id,
            job.id AS job_id,
            dept.id AS department_id,
            c.id AS contract_id,
            COUNT(otp.id) AS plans_count,
            COUNT(c.id) AS contracts_count,
            COUNT(emp.id) AS employees_count,
            comp.id AS company_id,
            comp.currency_id AS currency_id
        """

        for field in fields.values():
            select_ += field

        from_ = """
                hr_overtime_plan_line AS otpl
                JOIN hr_overtime_plan AS otp ON otp.id = otpl.overtime_plan_id
                JOIN hr_overtime_reason AS reason ON reason.id = otp.reason_id
                JOIN resource_calendar AS cal ON cal.id = otpl.resource_calendar_id
                JOIN hr_employee AS emp ON emp.id = otp.employee_id
                JOIN hr_contract AS c ON c.id = otpl.contract_id
                JOIN hr_overtime_rule AS rul ON rul.id = otpl.hr_overtime_rule_id
                JOIN hr_overtime_rule_code AS rulcode ON rulcode.id = otpl.rule_code_id
                JOIN res_company AS comp ON comp.id = otp.company_id
                LEFT JOIN resource_calendar_leaves AS gleave ON gleave.id = otpl.global_leave_id
                LEFT JOIN hr_department AS dept ON dept.id = c.department_id
                LEFT JOIN hr_job AS job ON job.id = c.job_id
                %s
        """ % from_clause
        
        where_ = """
            otpl.id > 0
            %s
        """ % where_clause

        groupby_ = """
            otpl.id,
            otpl.date_start,
            otpl.date_end,
            otp.recognition_mode,
            otpl.tz,
            cal.id,
            otp.id,
            emp.id,
            rul.id,
            rulcode.id,
            otpl.pay_rate,
            gleave.id,
            job.id,
            dept.id,
            c.id,
            comp.id %s
        """ % (groupby)

        return """%s (
            SELECT %s
            FROM %s
            WHERE %s
            GROUP BY %s
            )""" % (with_, select_, from_, where_, groupby_)

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

    def name_get(self):
        result = []
        for r in self:
            result.append(
                (r.id, _('%s from %s to %s') % (
                    r.employee_id.name, 
                    format_datetime(r.env, r.date_start, dt_format='short'), 
                    format_datetime(r.env, r.date_end, dt_format='short')
                )
            )
        )
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = [('employee_id.name', operator, name)]
        records = self.search(domain + args, limit=limit)
        return records.name_get()
