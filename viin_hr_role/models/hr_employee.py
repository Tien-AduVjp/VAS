from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # begin override
    role_id = fields.Many2one(tracking=True)
    # end override

    @api.constrains('department_id', 'role_id')
    def _check_role_department(self):
        for r in self:
            if r.role_id.department_id and r.department_id and r.department_id != r.role_id.department_id:
                raise ValidationError(_("Department Inconsistency! The role '%s' is applicable to the employees of the department '%s' only"
                                        " while the employee '%s' belongs to the department '%s'. Please change either the role or the"
                                        " employee department or revise the role's applicable department.")
                                        % (
                                            r.role_id.display_name,
                                            r.role_id.department_id.display_name,
                                            r.name,
                                            r.department_id.display_name
                                            )
                                        )
