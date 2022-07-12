from . import models
from odoo import api, SUPERUSER_ID


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    res_id = env.ref('stock.group_stock_user').id
    # if use odoo api to write, an error occurs related to recursive in Odoo 13.
    cr.execute(
        """
        UPDATE res_groups
        SET name = 'User', comment = ''
        WHERE id = %s
        """, (res_id,)
        )
