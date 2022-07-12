# -*- coding: utf-8 -*-

from odoo import tools
from odoo import fields, models


class HrEmployeeSkillReport(models.Model):
    _name = 'hr.employee.skill.report'
    _description = "Employee Skill Report"
    _auto = False
    _rec_name = 'employee_id'
    _order = 'employee_id, skill_id, expectation DESC, reach_progress DESC'

    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    job_id = fields.Many2one('hr.job', string='Job Position', readonly=True,
                             help="The current job position of the corresponding employee.")
    department_id = fields.Many2one('hr.department', string='Department', readonly=True,
                                    help="The current department of the corresponding employee.")
    grade_id = fields.Many2one('hr.employee.grade', string='Grade', readonly=True,
                               help="The current grade of the corresponding employee.")
    role_id = fields.Many2one('hr.role', string='Role', readonly=True,
                              help="The current role of the corresponding employee.")
    #TODO: rename field `rank_id` into `current_rank_id` in 15+
    rank_id = fields.Many2one('hr.rank', string='Current Rank', readonly=True,
                              help="The current rank of the corresponding employee.")
    expectation = fields.Selection([
        ('required', 'Required'),
        ('preferred', 'Preferred')], readonly=True, string='Expectation')
    # Employee's Skill
    skill_type_id = fields.Many2one('hr.skill.type', string='Skill Type', readonly=True)
    skill_id = fields.Many2one('hr.skill', string='Skill', readonly=True)
    current_skill_level_id = fields.Many2one(
        'hr.skill.level',
        string='Current Skill Level',
        readonly=True,
        help="Existing skills level of the corresponding employee.\n"
        "  If none, the employee is assumed to not have this skill currently.")
    current_level = fields.Integer(
        string='Current Level',
        readonly=True,
        group_operator="avg",
        help="Existing skills level progress of the corresponding employee.\n"
        " If none, the employee is assumed to not have this skill currently.")
    # Current Rank's Skill
    current_rank_skill_level_id = fields.Many2one(
        'hr.skill.level',
        string='Required Skill Level',
        readonly=True,
        help= "Skill level for current rank.\n"
            " If none, this skill is assumed to not available for current rank.")
    required_level = fields.Integer(
        string='Required Level',
        readonly=True,
        group_operator="avg",
        help= "Skill level progress for current rank.\n"
            " If none, this skill is assumed to not available for current rank.")
    reach_progress = fields.Integer(string='Current Rank Progress Reach', readonly=True, group_operator="avg")
    current_rank_skill_description = fields.Html(string='Current Rank Skill Description', readonly=True, translate=True)
    #Next Rank's Skill
    next_rank_id = fields.Many2one('hr.rank', string='Next Rank', readonly=True,
                              help="The next rank of the corresponding employee.")
    next_rank_skill_level_id = fields.Many2one('hr.skill.level', string='Next Rank Skill Level', readonly=True,
                                                help="The next rank skill level of the corresponding employee.")
    next_rank_level_required = fields.Integer(string='Next Rank Level', readonly=True, group_operator="avg")
    next_rank_reach_progress = fields.Integer(string='Next Rank Progress Reach', readonly=True, group_operator="avg")
    next_rank_skill_description = fields.Html(string='Next Rank Skill Description', readonly=True, translate=True)

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
            description.skill_type_id AS skill_type_id,
            description.skill_id AS skill_id,
            description.skill_level_id AS standard_skill_level_id,
            description.description as description
            FROM employee_skill_union AS u
            JOIN hr_skill_description AS description ON description.id = u.skill_description_id
        ),
        employee_next_rank_skill AS(
            SELECT
            row_number() OVER(
                ORDER BY
                skill_description.id,
                emp.id,
                skill_description.skill_type_id,
                skill_description.expectation,
                std.id
            ) AS id,
            emp.id AS employee_id,
            emp.rank_id AS rank_id,
            emp.company_id AS company_id,
            emp.department_id AS department_id,
            emp.job_id AS job_id,
            emp.role_id AS role_id,
            emp.grade_id AS grade_id,
            next_rank.id AS next_rank_id,
            skill_description.expectation AS expectation,
            skill_description.skill_id AS next_rank_skill_id,
            skill_description.skill_level_id AS next_rank_skill_level_id,
            skill_description.skill_type_id AS next_rank_skill_type_id,
            description.description as next_rank_skill_description,
            std.skill_id AS current_rank_skill_id,
            std.standard_skill_level_id AS current_rank_skill_level_id,
            std.skill_type_id AS current_rank_skill_type_id,
            std.description as current_rank_skill_description
            FROM hr_rank as next_rank
                JOIN hr_rank_hr_rank_skill_description_rel AS consolidated_skills ON consolidated_skills.rank_id = next_rank.id
                JOIN hr_rank_skill_description AS skill_description ON skill_description.id = consolidated_skills.rank_skill_description_id
                JOIN hr_skill_description AS description ON description.id = skill_description.skill_description_id
                JOIN hr_employee AS emp
                    ON next_rank.id = COALESCE(emp.next_rank_id,emp.rank_id) -- this will ensure when employee reach highest rank still having report skill
                LEFT JOIN employee_standard_skill AS std
                    ON std.employee_id = emp.id
                    AND std.skill_id = skill_description.skill_id
        )
        %s
        """ % with_clause
        )

        select_ = """
        nrs.id,
        nrs.employee_id,
        nrs.rank_id,
        nrs.company_id,
        nrs.department_id,
        nrs.job_id,
        nrs.grade_id,
        nrs.role_id,
        nrs.next_rank_id,
        nrs.expectation,
        COALESCE(employee_skill.skill_type_id,nrs.current_rank_skill_type_id,nrs.next_rank_skill_type_id) AS skill_type_id,
        COALESCE(employee_skill.skill_id,nrs.current_rank_skill_id,nrs.next_rank_skill_id) AS skill_id,


        -- Employee Skill
        employee_skill.skill_level_id AS current_skill_level_id,
        COALESCE(employee_level_progress.level_progress,0) AS current_level,

        -- Next Rank Skill
        nrs.next_rank_skill_level_id,
        COALESCE(next_rank_level_progress.level_progress,0) AS next_rank_level_required,
        CASE
            WHEN next_rank_level_progress.level_progress != 0
                AND COALESCE(employee_level_progress.level_progress,0) < next_rank_level_progress.level_progress
                THEN (COALESCE(employee_level_progress.level_progress,0) * 1.0 / next_rank_level_progress.level_progress) *100.0
            WHEN COALESCE(employee_level_progress.level_progress,0) >= next_rank_level_progress.level_progress
                THEN 100.0
            END AS next_rank_reach_progress,
        nrs.next_rank_skill_description,
        
        -- Current Rank Skill
        nrs.current_rank_skill_level_id,
        COALESCE(current_rank_level_progress.level_progress,0) AS required_level,
        CASE
            WHEN current_rank_level_progress.level_progress != 0 AND  COALESCE(employee_level_progress.level_progress,0) < current_rank_level_progress.level_progress
                THEN (COALESCE(employee_level_progress.level_progress,0) * 1.0 / current_rank_level_progress.level_progress) *100.0
            WHEN COALESCE(employee_level_progress.level_progress,0) >= current_rank_level_progress.level_progress
                THEN 100.0
            END AS reach_progress,
        nrs.current_rank_skill_description
        """

        for field in fields.values():
            select_ += field

        from_ = """
        employee_next_rank_skill AS nrs
        LEFT JOIN hr_employee AS emp ON emp.id = nrs.employee_id
        LEFT JOIN hr_employee_skill AS employee_skill
            ON employee_skill.employee_id = nrs.employee_id
            AND employee_skill.skill_id = COALESCE(nrs.current_rank_skill_id,nrs.next_rank_skill_id)
        LEFT JOIN hr_skill_level AS employee_level_progress
            ON employee_level_progress.id = employee_skill.skill_level_id
        LEFT JOIN hr_skill_level AS current_rank_level_progress
            ON current_rank_level_progress.id = nrs.current_rank_skill_level_id
        LEFT JOIN hr_skill_level AS next_rank_level_progress
            ON next_rank_level_progress.id = nrs.next_rank_skill_level_id
        %s
        """ % from_clause


        where_ = """
        emp.active = True
        %s
        """% (where,)


        groupby_ = """
        nrs.id,
        nrs.employee_id,
        nrs.rank_id,
        nrs.company_id,
        nrs.department_id,
        nrs.job_id,
        nrs.grade_id,
        nrs.role_id,
        nrs.next_rank_id,
        nrs.expectation,
        nrs.next_rank_skill_id,
        nrs.next_rank_skill_level_id,
        nrs.next_rank_skill_type_id,
        next_rank_level_progress.level_progress,
        nrs.current_rank_skill_id,
        nrs.current_rank_skill_level_id,
        nrs.current_rank_skill_type_id,
        current_rank_level_progress.level_progress,
        reach_progress,
        employee_skill.skill_type_id,
        employee_skill.skill_id,
        employee_skill.skill_level_id,
        employee_level_progress.level_progress,
        nrs.current_rank_skill_description,
        nrs.next_rank_skill_description
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
