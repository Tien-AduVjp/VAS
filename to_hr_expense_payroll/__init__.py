from odoo import api, SUPERUSER_ID
from . import models


def _generate_expense_salary_rules(env):
    companies = env['res.company'].search([])
    companies._generate_expense_salary_rules()
    companies._add_hr_expense_to_net_rule()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_expense_salary_rules(env)
