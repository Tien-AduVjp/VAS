from odoo import models, fields


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    role_ids = fields.One2many('hr.role', 'department_id', string='Roles',
                               help="The roles that are dedicated for this department.")
