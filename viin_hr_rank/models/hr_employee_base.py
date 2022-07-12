from odoo import models, fields, api


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    rank_id = fields.Many2one('hr.rank', string='Current Rank', ondelete='restrict', compute='_compute_rank', store=True,
                              help="Current rank of the employee which is computed automatically based on the selected level and role.")

    next_rank_id = fields.Many2one(related='rank_id.parent_id', store=True, string='Next Targeted Rank')

    @api.depends('role_id.rank_ids', 'grade_id.rank_ids')
    def _compute_rank(self):
        cadidates = self.env['hr.rank']._find(self.role_id, self.grade_id, '|')
        for r in self:
            r.rank_id = cadidates.filtered(lambda rk: rk.role_id == r.role_id and rk.grade_id == r.grade_id)[:1]
