from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    odoo_module_products = env['product.template'].search([('odoo_module_id', '!=', False)])
    if odoo_module_products:
        odoo_module_products._compute_default_code()
