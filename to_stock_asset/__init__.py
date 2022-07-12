from . import models
from . import reports
from . import wizard
from odoo import api, SUPERUSER_ID


def _add_column_asset_category_id(cr):
    """Add column asset_category_id to avoid call to compute method when installing / upgrade module"""

    cr.execute("""
        ALTER TABLE stock_move ADD COLUMN IF NOT EXISTS asset_category_id integer REFERENCES account_asset_category ON DELETE SET NULL;
    """)


def _fill_asset_category_data(env):
    """Fill asset_category_id data"""

    moves = env['stock.move'].search([
        ('location_dest_id.usage', '=', 'asset_allocation'),
        ('state', 'not in', ['done', 'cancel']),
        ('product_id.asset_category_id', '!=', False),
        ]
    )
    if moves:
        moves._compute_asset_category_id()


def pre_init_hook(cr):
    _add_column_asset_category_id(cr)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    warehouse_ids = env['stock.warehouse'].search([])
    for r in warehouse_ids:
        r._create_or_update_sequences_and_picking_types()

    _fill_asset_category_data(env)
