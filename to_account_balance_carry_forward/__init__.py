from . import models
from . import wizard
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.company'].search([('chart_template_id', '!=', False)])._assign_balance_carry_forward_journal()