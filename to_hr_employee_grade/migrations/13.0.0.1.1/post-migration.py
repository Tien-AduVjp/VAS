from odoo import api, SUPERUSER_ID


def _update_noupdate_records(env):
    env.ref('to_hr_employee_grade.intern_grade').write({
        'parent_id': env.ref('to_hr_employee_grade.trainee_grade').id
        })


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_noupdate_records(env)

