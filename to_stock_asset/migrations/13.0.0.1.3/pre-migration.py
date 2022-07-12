from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    types_need_update = env['stock.picking.type'].with_context(active_test=False).search([('code', '=', 'asset_allocation')])
    types_need_update.write({'show_reserved': True})
