from odoo import api, SUPERUSER_ID

from odoo.addons.to_stock_asset.__init__ import _fill_asset_category_data


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    _fill_asset_category_data(env)
