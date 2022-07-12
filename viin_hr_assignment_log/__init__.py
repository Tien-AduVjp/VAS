# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo import api, SUPERUSER_ID

from . import models


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    existing_assignments = env['user.assignment'].search([])
    for user in existing_assignments.mapped('user_id').filtered(lambda u: u.employee_ids):
        user_assignments = existing_assignments.filtered(lambda a: a.user_id == user)
        for company in user_assignments.mapped('company_id'):
            assignments = user_assignments.filtered(lambda a: a.company_id == company)
            assignments.write({
                'employee_id': user.with_company(company).employee_id,
                })
