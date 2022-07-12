# -*- coding: utf-8 -*-

from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    employee_ids = env['hr.employee'].search([('address_home_id', '!=', False)]).filtered(lambda e: e.address_home_id.company_type == 'person')
    for employee_id in employee_ids:
        if employee_id.birthday:
            if employee_id.address_home_id.dob != employee_id.birthday:
                employee_id.address_home_id.write({
                    'dob': employee_id.birthday
                    })
        else:
            if employee_id.address_home_id.dob:
                employee_id.write({
                    'birthday': employee_id.address_home_id.dob,
                    'dyob': employee_id.address_home_id.dyob,
                    'mob': employee_id.address_home_id.mob,
                    'yob': employee_id.address_home_id.yob
                    })
