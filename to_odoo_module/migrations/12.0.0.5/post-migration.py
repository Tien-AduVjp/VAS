from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    app_product_tmpl_ids = env['product.template'].with_context(active_test=False).search([('is_odoo_app', '=', True)])
    if app_product_tmpl_ids:
        app_product_tmpl_ids.write({'list_price': 0.0})
    env['git.branch'].cron_scan()
