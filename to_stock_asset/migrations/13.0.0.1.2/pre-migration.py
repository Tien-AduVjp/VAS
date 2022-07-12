from odoo.addons.to_stock_asset.__init__ import _add_column_asset_category_id


def migrate(cr, version):
    _add_column_asset_category_id(cr)
