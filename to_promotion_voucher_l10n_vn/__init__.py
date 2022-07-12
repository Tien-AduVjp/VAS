from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([('chart_template_id', '=', env.ref('l10n_vn.vn_template').id)])
    if companies:
        companies._update_promotion_voucher_properties_vietnam()
