from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # override
    grade_id = fields.Many2one(ondelete='restrict', tracking=True)

    @api.constrains('department_id', 'grade_id')
    def _check_grade_department(self):
        for r in self:
            if r.grade_id.department_id and r.department_id and r.department_id != r.grade_id.department_id:
                raise ValidationError(_("Department Inconsistency! The grade '%s' is applicable to the employees of the department '%s' only"
                                        " while the employee '%s' belongs to the department '%s'. Please change either the grade or the"
                                        " employee department or revise the grade's applicable department.")
                                        % (
                                            r.grade_id.display_name,
                                            r.grade_id.department_id.display_name,
                                            r.name,
                                            r.department_id.display_name
                                            )
                                        )
