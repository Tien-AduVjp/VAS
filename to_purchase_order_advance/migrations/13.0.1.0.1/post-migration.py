from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.payment'].search([('partner_type', '!=', 'supplier'),
                                   ('purchase_order_id', '!=', False)])\
                          .write({'purchase_order_id': False})
