from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    move_attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment')

    @api.depends('move_id', 'payment_id')
    def _compute_attachment(self):
        for record in self:
            record.move_attachment_ids = record.move_id.attachment_ids + record.statement_id.attachment_ids + record.payment_id.attachment_ids
