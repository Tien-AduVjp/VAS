from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sequence_edit = fields.Integer(compute='_get_sequence_edit', inverse='_set_sequence_edit', store=True)

    @api.depends('sequence')
    def _get_sequence_edit(self):
        for r in self:
            r.sequence_edit = r.sequence

    def _set_sequence_edit(self):
        for r in self:
            r.sequence = r.sequence_edit
