from odoo import fields, models


class QualityAlert(models.Model):
    _inherit = "quality.alert"

    picking_id = fields.Many2one('stock.picking', 'Operation')

    lot_id = fields.Many2one('stock.production.lot', 'Lot',
        domain="['|', ('product_id', '=', product_id), ('product_id.product_tmpl_id.id', '=', product_tmpl_id)]")
