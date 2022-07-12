from odoo import models, fields, api


class StockInventory(models.Model):
    _name = 'stock.inventory'
    _inherit = ['stock.inventory', 'barcodes.barcode_events_mixin']

    scan_location_id = fields.Many2one('stock.location', 'Scanned Location')

    @api.model
    def open_new_inventory(self):
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        if warehouse:
            inventory = self.env['stock.inventory'].create({
                'start_empty': True,
                'name': '%s - %s' % (warehouse.name, fields.Date.context_today(self)),
            })
        action = inventory.action_start()
        if self.product_ids:
            # no_create on product_id field
            action['views'] = [(self.env.ref('stock.stock_inventory_line_tree_no_product_create').id, 'tree')]
        else:
            # no product_ids => we're allowed to create new products in tree
            action['views'] = [(self.env.ref('stock.stock_inventory_line_tree').id, 'tree')]
        return action

    def _add_product(self, product, qty=1.0, lot_id=False):
        prd_line = self.line_ids.filtered(
            lambda l: l.product_id == product and
                      l.prod_lot_id.id == lot_id and
                      (not self.scan_location_id or self.scan_location_id == l.location_id)
        )[:1]
        if prd_line:
            prd_line.product_qty += qty
        else:
            company_id = self.company_id.id
            if not company_id:
                company_id = self.env.company.id
            location_id = self.scan_location_id.id or \
                          self.location_ids[:1].id or \
                          self.env['stock.location'].search([('usage', '=', 'internal')], order='id', limit=1).id
            domain = [('company_id', '=', company_id),
                      ('location_id', '=', location_id),
                      ('lot_id', '=', lot_id),
                      ('product_id', '=', product.id),
                      ('owner_id', '=', False),
                      ('package_id', '=', False)]
            self.line_ids += self.line_ids.new({
                'location_id': location_id,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'theoretical_qty': sum(self.env['stock.quant'].search(domain).mapped('quantity')),
                'product_qty': qty,
                'prod_lot_id': lot_id,
            })

    def on_barcode_scanned(self, barcode):
        if not barcode or self.state != 'draft':
            return

        product = self.env['product.product'].search([
            '|',
            ('barcode', '=', barcode),
            ('default_code', '=', barcode)
        ], limit=1)
        if product:
            self.product_ids = [(4, product.id)]
            return

        location = self.env['stock.location'].search([
            ('barcode', '=', barcode)
        ], limit=1)
        if location:
            self.location_ids = [(4, location.id)]
            return

    def on_validation_scanned(self, barcode):
        if not barcode or self.state != 'confirm':
            return

        product = self.env['product.product'].search([('barcode', '=', barcode)], limit=1)
        if product:
            return self._add_product(product)

        lot = self.env['stock.production.lot'].search([('name', '=', barcode)], limit=1)
        if lot:
            return self._add_product(lot.product_id, lot_id=lot.id)

        package = self.env['product.packaging'].search([('barcode', '=', barcode)], limit=1)
        if package and package.product_id:
            return self._add_product(package.product_id, package.qty)

        location = self.env['stock.location'].search([('barcode', '=', barcode)], limit=1)
        if location:
            return {'scan_location': (location.id, location.display_name)}


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    product_barcode = fields.Char(related='product_id.barcode')
