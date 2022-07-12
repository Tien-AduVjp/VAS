from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    odoo_module_versions = env['odoo.module.version'].search([])
    if odoo_module_versions:
        odoo_module_versions.rotate_token()
