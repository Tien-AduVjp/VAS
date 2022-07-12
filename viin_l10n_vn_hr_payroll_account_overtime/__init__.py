from odoo import api, SUPERUSER_ID

from . import models


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    companies = env['res.company'].sudo().search([('chart_template_id', '=', env.ref('l10n_vn.vn_template').id)])
    companies._update_ot_salary_rules_accounts()
