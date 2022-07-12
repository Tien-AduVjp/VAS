from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    relative_ids = fields.One2many('hr.employee.relative', 'employee_id', string='Related')
