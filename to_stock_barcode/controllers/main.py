from odoo import http, _
from odoo.http import request


class StockBarcodeController(http.Controller):

    @http.route('/stock_barcode/main_menu_scan', type='json', auth='user')
    def main_menu_scan(self, barcode, **kw):
        # First, try finding an existing picking corresponding to the barcode,
        # and open it if existing
        action = self._try_open_existing_picking(barcode)
        if action:
            return action
        warning = {'warning': _('There is no picking corresponding to the barcode %s') % barcode}

        # Then, try finding an internal location corresponding to the barcode,
        # and create new internal transfer from that location
        group_multi_locations = request.env.user.has_group('stock.group_stock_multi_locations')
        if group_multi_locations:
            action = self._try_open_new_picking(barcode)
            if action:
                return action
            warning = {'warning': _('There is no picking or location corresponding to the barcode %s') % barcode}

        # If none is found, display a warning
        return warning

    def _try_open_existing_picking(self, barcode):
        picking = request.env['stock.picking'].search([('name', '=', barcode),
                                                       ('state', 'in', ('partially_available', 'assigned'))], limit=1)
        if picking:
            return {'action': self._prepare_picking_action(picking.id)}
        return False

    def _try_open_new_picking(self, barcode):
        internal_loc = request.env['stock.location'].search([('barcode', '=', barcode),
                                                             ('usage', '=', 'internal')], limit=1)
        if internal_loc:
            warehouse = internal_loc.get_warehouse()
            picking_type = request.env['stock.picking.type'].search([('code', '=', 'internal'),
                                                                     ('warehouse_id', '=', warehouse.id)], limit=1)
            if not picking_type:
                picking_type = request.env['stock.picking.type'].search([('code', '=', 'internal'),
                                                                         ('warehouse_id', '=', False)], limit=1)
            if picking_type:
                picking = self._create_new_picking(picking_type.id, internal_loc.id, internal_loc.id)
                return {'action': self._prepare_picking_action(picking.id)}
            return {'warning': _('No internal operation type available. Please configure one and then try again.')}
        return False

    def _create_new_picking(self, picking_type_id, location_id, location_dest_id):
        picking = request.env['stock.picking'].create({
            'picking_type_id': picking_type_id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
        })
        picking.action_confirm()
        return picking

    def _prepare_picking_action(self, picking_id=False):
        action = request.env['ir.actions.act_window']._for_xml_id('to_stock_barcode.stock_picking_form_action')
        if picking_id:
            action.update(res_id=picking_id)
        return action

    @http.route('/stock_barcode/hide_message_demo', type='json', auth='user')
    def hide_message_demo(self, **kw):
        action = request.env.ref('to_stock_barcode.stock_barcode_main_action', raise_if_not_found=False)
        if action:
            action.sudo().write({'params': {'message_demo': False}})
