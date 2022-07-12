from odoo import api, SUPERUSER_ID

from . import models


def _map_specific_identification_to_fifo(env):
    """ This fallback method will be applied to all category
    that has been used specific identification to fifo.
    """
    categories = env['product.category'].search([('property_cost_method', '=', 'specific_identification')])
    categories.write({'property_cost_method': 'fifo'})


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _map_specific_identification_to_fifo(env)
