from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    vn_coa = env['account.chart.template']._get_installed_vietnam_coa_templates()
    companies = env['res.company'].sudo().search([('chart_template_id', 'in', vn_coa.ids)])
    companies._update_vietnam_salary_rules_accounts()
