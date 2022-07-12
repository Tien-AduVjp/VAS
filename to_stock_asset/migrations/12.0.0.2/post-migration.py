from odoo import api, SUPERUSER_ID


def _update_stock_picking_type_vals(env):
    types = env['stock.picking.type'].search([('code', '=', 'asset_allocation'), ('use_create_lots', '=', True)])
    if types:
        types.write({'use_create_lots': False})


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # to prevent stock picking to no create new lot/serial numbers when validating stock picking which has type as asset_allocation
    _update_stock_picking_type_vals(env)
