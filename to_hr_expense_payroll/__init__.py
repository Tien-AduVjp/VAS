# -*- coding: utf-8 -*-

from . import models
from . import wizard
from odoo import api, SUPERUSER_ID


def _generate_expense_salary_rules(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([])
    companies._generate_expense_salary_rules()
    companies._add_hr_expense_to_net_rule()
