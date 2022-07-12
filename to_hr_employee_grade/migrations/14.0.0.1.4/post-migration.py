from odoo import api, SUPERUSER_ID


def _update_noupdate_records(env):
    expert_grade = env.ref('to_hr_employee_grade.expert_grade', raise_if_not_found=False)
    if expert_grade:
        expert_grade.write({
            'parent_id': False
            })
    senior_grade = env.ref('to_hr_employee_grade.senior_grade', raise_if_not_found=False)
    if senior_grade:
        senior_grade.write({
            'parent_id': expert_grade.id
            })

    manager_grade= env.ref('to_hr_employee_grade.manager_grade', raise_if_not_found=False)
    if manager_grade:
        try:
            with env.cr.savepoint():
                manager_grade.unlink()
        except Exception as e:
            manager_grade_data = env['ir.model.data'].search([
                ('module', '=', 'to_hr_employee_grade'),
                ('name', '=', 'manager_grade'),
                ])
            if manager_grade_data:
                manager_grade_data.unlink()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_noupdate_records(env)

