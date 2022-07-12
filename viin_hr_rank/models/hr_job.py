from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrJob(models.Model):
    _inherit = 'hr.job'

    rank_line_ids = fields.One2many('hr.job.rank.line', 'job_id', string='Required Ranks')
    rank_ids = fields.Many2many('hr.rank', 'hr_job_hr_rank_rel', 'job_id', 'rank_id', string='Minimum Ranks',
                                compute='_compute_rank_ids', store=True,
                                help="The ranks at lowest levels that may require for the employees of this job position.")
    role_ids = fields.Many2many('hr.role', 'hr_job_hr_role_rel', 'job_id', 'role_id', string='Related Roles',
                                compute='_compute_role_ids')
    grade_ids = fields.Many2many('hr.employee.grade', 'hr_job_hr_employee_grade_rel', 'job_id', 'grade_id', string='Related Levels',
                                compute='_compute_grade_ids')

    @api.depends('rank_line_ids.rank_id')
    def _compute_rank_ids(self):
        for r in self:
            r.rank_ids = r.rank_line_ids.rank_id

    @api.depends('rank_line_ids.role_id')
    def _compute_role_ids(self):
        for r in self:
            r.role_ids = r.rank_line_ids.role_id

    @api.depends('rank_line_ids.grade_id')
    def _compute_grade_ids(self):
        for r in self:
            r.grade_ids = r.rank_line_ids.grade_id

    @api.constrains('rank_ids')
    def _check_rank_ids(self):
        for r in self:
            for role in r.rank_ids.role_id:
                if len(r.rank_ids.filtered(lambda rk: rk.role_id == role)) > 1:
                    raise UserError(_("You should select only one rank for the same role. A rank that requires less skills is preferred."))
