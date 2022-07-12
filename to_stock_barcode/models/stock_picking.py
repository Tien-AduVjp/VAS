from odoo import models, fields, api, _


class StockMoveLine(models.Model):
    _name = 'stock.move.line'
    _inherit = ['stock.move.line', 'barcodes.barcode_events_mixin']

    product_barcode = fields.Char(related='product_id.barcode')
    location_processed = fields.Boolean()

    def on_barcode_scanned(self, barcode):
        only_create_mode = self.env.context.get('only_create', False)
        serial_tracking = self.env.context.get('serial', False)

        if only_create_mode and serial_tracking:
            if barcode in self.mapped('lot_name'):
                return {'warning': {
                    'title': _('Warning'),
                    'message': _('Serial number %s has already been scanned.') % barcode,
                }}
            else:
                self.lot_name = barcode
                self.qty_done += 1.0

        elif only_create_mode and not serial_tracking:
            prd_line = self.filtered(lambda r: r.lot_name == barcode)[:1]
            if prd_line:
                prd_line.qty_done += 1.0
            else:
                self.lot_name = barcode
                self.qty_done += 1.0

        elif not only_create_mode:
            lots_visible = False
            picking = self.picking_id
            product = self.product_id
            if picking.picking_type_id and product.tracking != 'none':
                lots_visible = picking.picking_type_id.use_create_lots or picking.picking_type_id.use_existing_lots
            prd_line = self.filtered(lambda r: r.lot_id.name == barcode)[:1]
            if prd_line:
                if serial_tracking and prd_line.qty_done == 1.0:
                    return {'warning': {
                        'title': _('Warning'),
                        'message': _('Serial number %s has already been scanned.') % barcode,
                    }}
                else:
                    prd_line.qty_done += 1.0
                    self.lots_visible = lots_visible
            else:
                lot = self.env['stock.production.lot'].search([('product_id', '=', product.id),
                                                               ('name', '=', barcode)], limit=1)
                if lot:
                    self.qty_done += 1.0
                    self.lot_id = lot.id
                    self.lots_visible = lots_visible
                else:
                    if only_create_mode:
                        lot = self.env['stock.production.lot'].with_context({'mail_create_nosubscribe': True}).create({
                            'name': barcode,
                            'product_id': product.id
                        })
                        self.qty_done += 1.0
                        self.lot_id = lot.id
                        self.lots_visible = not serial_tracking
                    else:
                        return {'warning': {
                            'title': _('Lot doesn\'t exist'),
                            'message': _('There is no production lot for %s corresponding to the barcode %s') % (product.name, barcode),
                        }}


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'barcodes.barcode_events_mixin']

    def _prepare_stock_move_line_vals(self, product, uom_id, location, location_dest, qty_done, uom_qty, picking_type_lots):
        self.ensure_one()
        return {
            'product_id': product.id,
            'product_uom_id': uom_id.id,
            'location_id': location.id,
            'location_dest_id': location_dest.id,
            'qty_done': qty_done,
            'product_uom_qty': uom_qty,
            'lots_visible': picking_type_lots,
        }

    def _prepare_stock_move_line_package_vals(self, packop, qty_done):
        self.ensure_one()
        uom_qty = packop.product_uom_qty - qty_done
        picking_type_lots = packop.product_id.tracking != 'none'
        vals = self._prepare_stock_move_line_vals(packop.product_id, packop.product_uom_id, packop.location_id,
                                                  packop.location_dest_id, 0.0, uom_qty, picking_type_lots)
        vals.update({'package_id': packop.package_id.id})
        return vals

    def get_candidates_from_barcode(self, barcode):
        product_id = self.env['product.product'].search([('barcode', '=', barcode)])
        candidates = self.env['stock.move.line'].search([
            ('picking_id', 'in', self.ids),
            ('product_barcode', '=', barcode),
            ('location_processed', '=', False),
            ('result_package_id', '=', False),
        ])
        action_ctx = dict(self.env.context,
                          default_picking_id=self.id,
                          serial=self.product_id.tracking == 'serial',
                          default_product_id=product_id.id,
                          candidates=candidates.ids)
        view_id = self.env.ref('to_stock_barcode.stock_barcode_lot_form').id
        return {
            'name': _('Lot/Serial Number Details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock_barcode.lot',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': action_ctx
        }

    def scan_new_product(self, barcode):
        product_id = self.env['product.product'].search([('barcode', '=', barcode)])
        if not product_id or product_id.tracking == 'none':
            return self.on_barcode_scanned(barcode)
        else:
            return self.get_candidates_from_barcode(barcode)

    def on_barcode_scanned(self, barcode):
        if not self.env.company.nomenclature_id:
            if self._try_add_product(barcode):
                return
            if self._try_add_package_product(barcode):
                return
            if self._try_add_source_package(barcode):
                return
            if self._try_add_destination_package(barcode):
                return
            if self._try_add_destination_location(barcode):
                return
        else:
            parsed = self.env.company.nomenclature_id.parse_barcode(barcode)
            if parsed['type'] in ['weight', 'product']:
                if parsed['type'] == 'weight':
                    product_barcode = parsed['base_code']
                    qty = parsed['value']
                elif parsed['type'] == 'product':
                    product_barcode = parsed['code']
                    qty = 1.0
                if self._try_add_product(product_barcode, qty):
                    return

            elif parsed['type'] == 'package':
                if self._try_add_source_package(parsed['code']):
                    return
                if self._try_add_destination_package(parsed['code']):
                    return

            elif parsed['type'] == 'location':
                if self._try_add_destination_location(parsed['code']):
                    return

        return {'warning': {
            'title': _('Barcode doesn\'t exist'),
            'message': _('Barcode %s does not correspond to any product, package or location.') % {
                'barcode': barcode}
        }}

    def _add_product(self, product, qty=1.0):
        prd_lines = self.move_line_ids.filtered(
            lambda r: r.product_id.id == product.id and not r.result_package_id and not r.location_processed)
        if prd_lines:
            if not prd_lines[0].lots_visible:
                new_line = False
                last_line = False
                for line in prd_lines:
                    last_line = line
                    if line.product_uom_qty > line.qty_done:
                        new_line = line
                        break
                prd_line = new_line or last_line
                prd_line.qty_done += qty
        else:
            lots_visible = product.tracking != 'none' and (self.picking_type_id.use_create_lots or self.picking_type_id.use_existing_lots)
            qty_done = (product.tracking == 'none' and lots_visible) and qty or 0.0
            vals = self._prepare_stock_move_line_vals(product, product.uom_id, self.location_id, self.location_dest_id,
                                                      qty_done, 0.0, lots_visible)
            vals.update({'state': 'assigned'})
            new_move_line = self.env['stock.move.line'].new(vals)
            if self.show_reserved:
                self.move_line_ids_without_package += new_move_line
            else:
                self.move_line_nosuggest_ids += new_move_line
        return True

    def _try_add_product(self, barcode, qty=1.0):
        product = self.env['product.product'].search([
            '|',
            ('barcode', '=', barcode),
            ('default_code', '=', barcode)
        ], limit=1)
        if product:
            return self._add_product(product, qty)
        return False

    def _try_add_package_product(self, barcode):
        package = self.env['product.packaging'].search([('barcode', '=', barcode)], limit=1)
        if package.product_id:
            return self._add_product(package.product_id, package.qty)
        return False

    def _try_add_source_package(self, barcode):
        src_package = self.env['stock.quant.package'].search([
            ('name', '=', barcode),
            ('location_id', 'child_of', self.location_id.id)
        ], limit=1)
        if src_package:
            pkg_lines = self.move_line_ids.filtered(
                lambda r: r.package_id.id == src_package.id and r.result_package_id.id == src_package.id)
            for line in pkg_lines:
                line.qty_done = line.product_uom_qty
            return pkg_lines and True or False
        return False

    def _try_add_destination_package(self, barcode):
        dest_package = self.env['stock.quant.package'].search([
            ('name', '=', barcode),
            '|',
            ('location_id', '=', False),
            ('location_id', 'child_of', self.location_dest_id.id)
        ], limit=1)
        if dest_package:
            pkg_lines = self.move_line_ids.filtered(lambda r: not r.result_package_id and r.qty_done > 0)
            for line in pkg_lines:
                if line.qty_done < line.product_uom_qty:
                    vals = self._prepare_stock_move_line_package_vals(line, line.qty_done)
                    vals.update({
                        'result_package_id': dest_package.id
                    })
                    self.move_line_ids += self.move_line_ids.new(vals)
                    line.product_uom_qty = line.qty_done
                line.result_package_id = dest_package.id
            return True
        return False

    def _try_add_destination_location(self, barcode):
        location = self.env['stock.location'].search([
            '|',
            ('name', '=', barcode),
            ('barcode', '=', barcode),
            ('id', 'child_of', self.location_dest_id.id)
        ], limit=1)
        if location:
            loc_lines = self.move_line_ids.filtered(lambda r: not r.location_processed and r.qty_done > 0)
            for line in loc_lines:
                if line.qty_done < line.product_uom_qty:
                    vals = self._prepare_stock_move_line_package_vals(line, line.qty_done)
                    vals.update({
                        'location_dest_id': location.id,
                        'location_processed': True,
                    })
                    self.move_line_ids += self.move_line_ids.new(vals)
                    line.product_uom_qty = line.qty_done
                line.location_dest_id = location.id
                line.location_processed = True
            return True
        return False
