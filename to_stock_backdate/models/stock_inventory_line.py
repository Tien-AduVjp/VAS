from odoo import models, api


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    
    @api.depends('location_id', 'product_id', 'package_id', 'product_uom_id', 'company_id', 'prod_lot_id', 'partner_id', 'inventory_id.date')
    def _compute_theoretical_qty(self):
        for r in self:
            theoretical_qty = 0
            if r.product_id:
                theoretical_qty = r.with_context(to_date=r.inventory_id.date,
                                                 location=r.location_id.id,
                                                 lot_id=r.prod_lot_id.id,
                                                 owner_id=r.partner_id.id,
                                                 package_id=r.package_id.id,
                                                 compute_child=False).product_id.qty_available
            r.theoretical_qty = theoretical_qty
