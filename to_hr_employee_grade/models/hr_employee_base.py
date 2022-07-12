from odoo import models, fields


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    grade_id = fields.Many2one('hr.employee.grade', string='Grade',
                               domain="['&', '|', ('department_id', '=', department_id), ('department_id', '=', False), '|', ('company_id', '=', False), ('company_id', '=', current_company_id)]")
