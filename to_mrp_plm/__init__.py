from odoo import api, SUPERUSER_ID

from . import models


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Enable Work Orders for MRP application
    config = env['res.config.settings'].create({
        'group_mrp_routings': True
        })
    config.execute()
