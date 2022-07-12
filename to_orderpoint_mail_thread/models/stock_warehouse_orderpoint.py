from odoo import models, fields


class StockWarehouseOrderpoint(models.Model):
    _name = 'stock.warehouse.orderpoint'
    _inherit = ['stock.warehouse.orderpoint', 'mail.thread']

    name = fields.Char(tracking=True)
    active = fields.Boolean(tracking=True)
    warehouse_id = fields.Many2one(tracking=True)
    location_id = fields.Many2one(tracking=True)
    product_id = fields.Many2one(tracking=True)
    product_uom = fields.Many2one(tracking=True)
    product_min_qty = fields.Float(tracking=True)
    product_max_qty = fields.Float(tracking=True)
    qty_multiple = fields.Float(tracking=True)
    group_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)

    def action_read_order_point(self):
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.warehouse.orderpoint',
            'res_id': self.id,
        }
