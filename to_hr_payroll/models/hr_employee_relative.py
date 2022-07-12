from odoo import fields, models


class HrEmployeeRelative(models.Model):
    _inherit = 'hr.employee.relative'

    is_dependant = fields.Boolean('Is Dependant', default=False)
