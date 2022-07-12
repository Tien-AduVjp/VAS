from odoo import models, fields, api


class HrJobRankLine(models.Model):
    _name = 'hr.job.rank.line'
    _description = "Hr Job Rank Line"
    _order = 'rank_id, job_id, id'

    job_id = fields.Many2one('hr.job', string='Job Position', required=True, ondelete='cascade')
    role_id = fields.Many2one('hr.role', string='Role', required=True,)
    grade_id = fields.Many2one('hr.employee.grade', string='Level', required=True)
    rank_id = fields.Many2one('hr.rank', string='Rank', compute='_compute_rank_id', store=True, ondelete='cascade')

    _sql_constraints = [
        (
            'role_grade_uniq',
            'unique(role_id, job_id)',
            "Role must be unique per job position!"
            ),
    ]

    @api.depends('role_id.rank_ids', 'grade_id.rank_ids')
    def _compute_rank_id(self):
        cadidates = self.env['hr.rank']._find(self.role_id, self.grade_id, '|')
        for r in self:
            r.rank_id = cadidates.filtered(lambda rk: rk.role_id == r.role_id and rk.grade_id == r.grade_id)[:1]

