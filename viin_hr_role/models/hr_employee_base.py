from odoo import models, fields, api


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    role_id = fields.Many2one('hr.role', string='Role', ondelete='restrict',
                              domain="['&', '|', ('department_id', '=', department_id), ('department_id', '=', False), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
