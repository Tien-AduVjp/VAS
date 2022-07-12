from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    move_lines = env['account.move'].search([
        ('type', 'in', ['out_refund', 'out_receipt', 'out_invoice'])
    ]).invoice_line_ids
    move_lines._compute_odoo_module_version()
