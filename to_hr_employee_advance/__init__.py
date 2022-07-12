from . import models
from . import wizard
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([('chart_template_id', '!=', False)])
    if companies:
        companies.create_employee_advance_journal_if_not_exists()
