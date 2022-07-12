from odoo import fields, models


class StockScrap(models.Model):
    _name = 'stock.scrap'
    _inherit = ['stock.scrap', 'barcodes.barcode_events_mixin']

    product_barcode = fields.Char(related='product_id.barcode', string='Barcode')

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        product = self.env['product.product'].search(['|', ('barcode', '=', barcode), ('default_code', '=', barcode)], limit=1)
        if product:
            if self.product_id == product:
                self.scrap_qty += 1
            else:
                self.product_id = product
                self.scrap_qty = 1
                self.lot_id = False
            return
        lot = self.env['stock.production.lot'].search([('name', '=', barcode)])
        if lot:
            if self.lot_id == lot:
                self.scrap_qty += 1
            else:
                self.product_id = lot.product_id
                self.scrap_qty = 1
                self.lot_id = lot.id
