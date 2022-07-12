# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_wrong_user_assignment_employee(env):
    env.cr.execute("""
    UPDATE user_assignment AS ua
    SET employee_id = emp.id
    FROM hr_employee AS emp
    WHERE emp.user_id = ua.user_id
    """)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_wrong_user_assignment_employee(env)

