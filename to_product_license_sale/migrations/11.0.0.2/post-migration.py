from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # fill licenses for lines that missing licenses
    sol_ids = env['sale.order.line'].search([
        ('product_id.product_license_version_ids', '!=', False),
        ('product_license_version_ids', '=', False)])

    for line in sol_ids:
        line.write({'product_license_version_ids': [(6, 0, line.product_id.product_license_version_ids.ids)]})
