from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    lines = env['account.move.line'].search([
        ('display_type', '=', False),
        ('move_id.move_type', 'in', ('out_refund', 'in_refund')),
        ('move_id.reversed_entry_id', '!=', False),
        ('exclude_from_invoice_tab', '=', False)
    ])
    for line in lines:
        reverse_line = line.move_id.reversed_entry_id.invoice_line_ids.filtered(
            lambda r: r.product_id == line.product_id or r.name == line.name)
        if len(reverse_line) == 1:
            line.write({'reversed_move_line_id': reverse_line.id})
