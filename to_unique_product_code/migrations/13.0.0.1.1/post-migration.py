from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.company'].search([]).write({'check_unique_product_default_code': True})
