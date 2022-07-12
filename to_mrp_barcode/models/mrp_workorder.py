from odoo import api, models


class MrpWorkorder(models.Model):
    _name = 'mrp.workorder'
    _inherit = ['mrp.workorder', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        barcode_nomenclature = self.env.company.nomenclature_id
        if not barcode_nomenclature:
            if self.product_id.barcode == barcode:
                if self.qty_producing < self.qty_production:
                    self.qty_producing += 1
                else:
                    self.qty_producing = 1
            elif self.product_id.tracking != 'none':
                lot = self.env['stock.production.lot'].search([('name', '=', barcode)], limit=1)
                if lot.product_id == self.product_id:
                    self.finished_lot_id = lot
        else:
            parsed_result = barcode_nomenclature.parse_barcode(barcode)
            if parsed_result['type'] in ['weight', 'product']:
                if parsed_result['type'] == 'weight':
                    product_barcode = parsed_result['base_code']
                    qty = parsed_result['value']
                else:  # product
                    product_barcode = parsed_result['code']
                    qty = 1.0
                if self.product_id.barcode == product_barcode:
                    if self.qty_producing + qty <= self.qty_production:
                        self.qty_producing += qty
                    else:
                        self.qty_producing = qty
            elif parsed_result['type'] == 'lot':
                lot = self.env['stock.production.lot'].search([('name', '=', parsed_result["code"])], limit=1)
                if lot:
                    if lot.product_id == self.product_id:
                        self.finished_lot_id = lot
                elif not self.finished_lot_id:
                    self.finished_lot_id = self.env['stock.production.lot'].create({
                        'product_id': self.product_id.id,
                        'name': parsed_result['code'],
                        'company_id': self.env.company.id
                        })

    def button_start1(self):
        return self.button_start()

    def button_start2(self):
        return self.button_start()

    def button_start3(self):
        return self.button_start()
