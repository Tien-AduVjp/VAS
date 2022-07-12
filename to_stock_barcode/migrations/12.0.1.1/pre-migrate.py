from odoo import api, SUPERUSER_ID


def migrate(cr, registry):
    """ Unlink old view of res.config.settings to avoid error during upgrading """
    env = api.Environment(cr, SUPERUSER_ID, {})
    old_view = env.ref('to_stock_barcode.res_config_settings_view_form', raise_if_not_found=False)
    if old_view:
        old_view.unlink()
