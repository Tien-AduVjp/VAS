# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _compute_involve_employees(env):
    timesheets_requests = env['approval.request'].search([('type', '=', 'timesheets')])
    timesheets_requests._compute_involve_employee_ids()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _compute_involve_employees(env)

