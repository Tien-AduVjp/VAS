from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    # override
    grade_ids = fields.One2many('hr.employee.grade', 'department_id', string='Grades',
                                help="The grades that are dedicated for this department.")
    grades_count = fields.Integer(string='Grades Count', compute='_compute_grades_count')
    
    @api.depends('grade_ids')
    def _compute_employees_count(self):
        grade_data = self.env['hr.employee.grade'].read_group([('department_id', 'in', self.ids)], ['department_id'], ['department_id'])
        mapped_data = dict((data['department_id'][0], data['department_id_count']) for data in grade_data)
        for r in self:
            r.grades_count = mapped_data.get(r.id, 0)
