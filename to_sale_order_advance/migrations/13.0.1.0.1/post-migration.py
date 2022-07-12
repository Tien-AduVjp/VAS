from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.payment'].search([('partner_type', '!=', 'customer'),
                                   ('sale_order_id', '!=', False)])\
                          .write({'sale_order_id': False})
