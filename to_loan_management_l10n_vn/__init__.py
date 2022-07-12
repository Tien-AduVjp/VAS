from . import models

from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    vn_chart = env.ref('l10n_vn.vn_template')
    env['res.company'].search([('chart_template_id', '=', vn_chart.id)])._update_vn_params()
