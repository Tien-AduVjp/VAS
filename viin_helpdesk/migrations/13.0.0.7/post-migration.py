from odoo import api, SUPERUSER_ID, tools


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    #fix attachment ownership
    tickets = env['helpdesk.ticket'].search([])
    tickets._reattaching_attachments_to_ticket()
