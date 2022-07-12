from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """ Upgrade to_quality module first to avoid error on upgrading """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.module.module'].search([('name', '=', 'to_quality')], limit=1).button_upgrade()
