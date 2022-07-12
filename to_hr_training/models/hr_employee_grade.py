from odoo import models, fields, api
  
  
class HrEmployeeGrade(models.Model):
    _inherit = 'hr.employee.grade'

    require_training_ids = fields.One2many('hr.require.training', 'grade_id', string='Required Courses')

    def _recompute_course(self):
        """
        call method _compute_training_line_ids() again
        """
        employees = self.env['hr.employee'].search([('grade_id', 'parent_of', self.ids)])
        employees._compute_training_line_ids()

    @api.model_create_multi
    def create(self, vals_list):
        res = super(HrEmployeeGrade, self).create(vals_list)
        res._recompute_course()
        return res

    def write(self, vals):
        res = super(HrEmployeeGrade, self).write(vals)
        if 'parent_id' in vals or 'child_ids' in vals:
            self._recompute_course()
        return res

    def unlink(self):
        grade_ids = self.ids
        employees = self.env['hr.employee'].search([('grade_id', 'parent_of', grade_ids)])
        res = super(HrEmployeeGrade, self).unlink()
        employees._compute_training_line_ids()
        return  res
