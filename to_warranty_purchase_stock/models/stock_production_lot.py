from odoo import  fields, models, api


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    warranty_start_date = fields.Date(string='Warranty Start Date', compute='_compute_warranty_start_date', readonly=False, store=True)

    @api.depends('purchase_order_id')
    def _compute_warranty_start_date(self):
        for r in self:
            if not r.warranty_start_date:
                r.warranty_start_date = r.purchase_order_id.effective_date
            else:
                r.warranty_start_date = r.warranty_start_date
