from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for company_id in env['res.company'].search([('chart_template_id', '!=', False)]):
        company_id.create_landed_cost_journal_if_not_exists()
