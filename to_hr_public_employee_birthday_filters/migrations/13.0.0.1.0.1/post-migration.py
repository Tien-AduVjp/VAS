from odoo import api, SUPERUSER_ID


def _restore_birthday_on_hr_employee_public_from_res_partner(env):
    employee_ids = env['hr.employee.public'].search([('address_id', '!=', False)]).filtered(lambda e: e.address_id.company_type == 'person')
    for employee_id in employee_ids:
        if employee_id.address_id.dob:
            employee_id.write({
                'birthday': employee_id.address_id.dob,
                'dyob': employee_id.address_id.dyob,
                'mob': employee_id.address_id.mob,
                'yob': employee_id.address_id.yob
                })

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _restore_birthday_on_hr_employee_public_from_res_partner(env)

