from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sequence_edit = fields.Integer(compute='_compute_sequence_edit', inverse='_inverse_sequence_edit', store=True)

    @api.depends('sequence')
    def _compute_sequence_edit(self):
        for r in self:
            r.sequence_edit = r.sequence

    def _inverse_sequence_edit(self):
        for r in self:
            r.sequence = r.sequence_edit
