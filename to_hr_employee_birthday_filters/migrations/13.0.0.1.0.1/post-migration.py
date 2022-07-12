from odoo import api, SUPERUSER_ID


def _restore_birthday_on_hr_employee_from_res_partner(env):
    employee_ids = env['hr.employee'].search([('address_home_id', '!=', False)]).filtered(lambda e: e.address_home_id.company_type == 'person')
    for employee_id in employee_ids:
        if employee_id.address_home_id.dob:
            employee_id.write({
                'birthday': employee_id.address_home_id.dob,
                'dyob': employee_id.address_home_id.dyob,
                'mob': employee_id.address_home_id.mob,
                'yob': employee_id.address_home_id.yob
                })

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _restore_birthday_on_hr_employee_from_res_partner(env)

