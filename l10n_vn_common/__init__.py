from odoo import api, SUPERUSER_ID
from . import models


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Disable anglo saxon
    env['res.company']._disable_anglo_saxon_for_vn_coa()
    # Set the tax groups is vat
    env['account.tax.group']._set_tax_group_is_vat_vietnam()
