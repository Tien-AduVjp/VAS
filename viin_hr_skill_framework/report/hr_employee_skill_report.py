# -*- coding: utf-8 -*-

from odoo import tools
from odoo import fields, models


class HrEmployeeSkillReport(models.Model):
    _name = 'hr.employee.skill.report'
    _description = "Employee Skill Report"
    _auto = False
    _rec_name = 'employee_id'
    _order = 'employee_id, skill_id, expectation DESC, reach_progress DESC'

    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    job_id = fields.Many2one('hr.job', string='Job Position', readonly=True,
                             help="The current job position of the corresponding employee.")
    department_id = fields.Many2one('hr.employee', string='Department', readonly=True,
                                    help="The current department of the corresponding employee.")
    grade_id = fields.Many2one('hr.employee.grade', string='Grade', readonly=True,
                               help="The current grade of the corresponding employee.")
    role_id = fields.Many2one('hr.role', string='Role', readonly=True,
                              help="The current role of the corresponding employee.")
    rank_id = fields.Many2one('hr.rank', string='Rank', readonly=True,
                              help="The current rank of the corresponding employee.")
    expectation = fields.Selection([
        ('required', 'Required'),
        ('preferred', 'Preferred')], readonly=True, string='Expectation')
    skill_type_id = fields.Many2one('hr.skill.type', string='Skill Type', readonly=True)
    skill_id = fields.Many2one('hr.skill', string='Skill', readonly=True)
    standard_skill_level_id = fields.Many2one('hr.skill.level', string='Required Skill Level', readonly=True)
    required_level = fields.Integer(string='Required Level', readonly=True, group_operator="avg")
    current_skill_level_id = fields.Many2one('hr.skill.level', string='Current Skill Level', readonly=True)
    current_level = fields.Integer(string='Current Level', readonly=True, group_operator="avg")
    reach_progress = fields.Integer(string='Progress Reach', readonly=True, group_operator="avg")
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause='', where=''):
        with_ = ("""
        WITH employee_skill_union AS(
            SELECT *, 'required' AS expectation FROM employee_skill_description_required_rel
            UNION ALL
            SELECT *, 'preferred' AS expectation FROM employee_skill_description_preferred_rel
        ),
        employee_standard_skill AS (
            SELECT
            row_number() OVER(
                ORDER BY
                description.id,
                u.employee_id,
                description.skill_type_id,
                description.skill_id,
                u.expectation
            ) AS id,
            u.employee_id,
            u.expectation,
            description.skill_type_id AS skill_type_id,
            description.skill_id AS skill_id,
            description.skill_level_id AS standard_skill_level_id
            FROM employee_skill_union AS u
            JOIN hr_skill_description AS description ON description.id = u.skill_description_id
        )
        %s
        """ % with_clause
        )

        select_ = """
        std.id,
        std.employee_id,
        job.id AS job_id,
        dept.id AS department_id,
        grade.id AS grade_id,
        role.id AS role_id,
        rank.id AS rank_id,
        std.expectation,
        std.skill_type_id,
        std.skill_id,
        std.standard_skill_level_id,
        std_level.level_progress AS required_level,
        act.skill_level_id AS current_skill_level_id,
        coalesce(reached_level.level_progress, 0) AS current_level,
        CASE WHEN std_level.level_progress != 0
            THEN (coalesce(reached_level.level_progress, 0) * 1.0 / std_level.level_progress) *100.0
            ELSE 100.0
            END AS reach_progress,
        c.id AS company_id
        """

        for field in fields.values():
            select_ += field

        from_ = """
        employee_standard_skill AS std
        JOIN hr_employee AS emp ON emp.id = std.employee_id
        LEFT JOIN hr_job AS job ON job.id = emp.job_id
        LEFT JOIN hr_department AS dept ON dept.id = emp.department_id
        LEFT JOIN hr_employee_grade AS grade ON grade.id = emp.grade_id
        LEFT JOIN hr_role AS role ON role.id = emp.role_id
        LEFT JOIN hr_rank AS rank ON rank.id = emp.rank_id
        LEFT JOIN res_company AS c ON c.id = emp.company_id
        LEFT JOIN hr_employee_skill AS act
            ON act.employee_id = std.employee_id
                AND act.skill_type_id = std.skill_type_id
                AND act.skill_id = std.skill_id
        LEFT JOIN hr_skill_level AS std_level
            ON std_level.id = std.standard_skill_level_id
        LEFT JOIN hr_skill_level AS reached_level
            ON reached_level.id = act.skill_level_id
        %s
        """ % from_clause
        
        
        where_ = """
        emp.active = True
        %s
        """% (where,)
        

        groupby_ = """
        std.id,
        std.employee_id,
        job.id,
        dept.id,
        std.expectation,
        std.skill_type_id,
        std.skill_id,
        std.standard_skill_level_id,
        std_level.level_progress,
        act.skill_level_id,
        reached_level.level_progress,
        c.id,
        grade.id,
        role.id,
        rank.id
        %s
        """ % (groupby,)

        return """%s (
            SELECT %s
            FROM %s
            WHERE %s
            GROUP BY %s
            )""" % (with_, select_, from_, where_,groupby_)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
