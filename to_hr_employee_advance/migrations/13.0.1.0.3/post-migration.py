from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['employee.advance.reconcile'].search([('state', 'in', ('confirm', 'done'))])._reconcile()
