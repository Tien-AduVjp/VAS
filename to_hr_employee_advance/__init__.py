from odoo import api, SUPERUSER_ID
from . import models
from . import wizards


def _create_employee_advance_journal(env):
    companies = env['res.company']
    companies._generate_employee_advance_account_journals()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _create_employee_advance_journal(env)
