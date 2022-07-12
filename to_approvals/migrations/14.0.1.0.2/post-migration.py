from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['approval.request'].search([('state', 'in', ('draft', 'confirm', 'refuse'))])._compute_mimimum_approvals()
