from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    repair_fee_line_ids = fields.Many2many(
        'repair.fee',
        'repair_fee_line_invoice_rel',
        'invoice_line_id', 'repair_fee_line_id',
        string='Repair Fee Lines', readonly=True, copy=False)
