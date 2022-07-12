from odoo import models, fields


class EmployeeGrade(models.Model):
    _inherit = 'hr.employee.grade'

    rank_ids = fields.One2many('hr.rank', 'grade_id', string='Ranks', readonly=True)

    def write(self, vals):
        """
        Override to recompute related ranks' parent
        """
        org_ranks = self.env['hr.rank']
        if 'parent_id' in vals:
            org_ranks = self.rank_ids
        res = super(EmployeeGrade, self).write(vals)
        org_ranks |= self.rank_ids
        org_ranks._compute_parent_id()
        return res
