from odoo import api, fields, models


class QualityPoint(models.Model):
    _inherit = "quality.point"

    picking_type_id = fields.Many2one('stock.picking.type', string="Stock Operation Type")

