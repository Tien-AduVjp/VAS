from . import models
from odoo import api, SUPERUSER_ID


def _match_odoo_versions_with_product_attributes(env):
    odoo_versions = env['odoo.version'].search([('product_attribute_value_id', '=', False)])
    for odoo_version in odoo_versions:
        odoo_version.write({'product_attribute_value_id': odoo_version._create_if_not_exists_product_attribute_value().id})


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _match_odoo_versions_with_product_attributes(env)
