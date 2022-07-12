import json

from odoo import models, fields


class HrRoleDashboard(models.Model):
    _inherit = 'hr.role'

    hr_employee_skill_report_ids = fields.One2many('hr.employee.skill.report', 'role_id', string='Skill Report Entries')

    def get_dashboard_datas(self):
        res = super(HrRoleDashboard, self).get_dashboard_datas()
        grades = []
        for grade in self.sudo().hr_employee_skill_report_ids.grade_id:
            employees = self.sudo().hr_employee_skill_report_ids.filtered(lambda r: r.grade_id.id == grade.id).employee_id
            grades.append({
                'action': {
                    'data-name': 'action_view_employees',
                    'data-context': json.dumps({'grade_id': grade.id}),
                    },
                'name': grade.display_name,
                'employee_ids': employees.ids,
                'employees_count': len(employees)
                })
        res.update({
            'grades': grades,
            })
        return res
