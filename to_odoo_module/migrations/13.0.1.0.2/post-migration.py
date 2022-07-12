from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    odoo_app_products = env['product.template'].search([('is_odoo_app', '=', True)])
    if odoo_app_products:
        odoo_app_products._compute_odoo_module()
