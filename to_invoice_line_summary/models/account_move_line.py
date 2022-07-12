from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_line_summary_id = fields.Many2one('invoice.line.summary', string="Invoice Lines Summary", copy=False)
