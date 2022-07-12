from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    voucher_receipt_picking_type_id = fields.Many2one('stock.picking.type', string='Promotion Voucher Receipt Type', help="The stock operation type for"
                                                      " grouping gift / promotion vouchers receiving into this warehouse")

    def _prepare_voucher_receipt_picking_type(self):
        src_location = self.env['stock.location'].search([('usage', '=', 'transit'), ('company_id', '=', self.company_id.id)], limit=1)
        if not src_location:
            src_location = self.env.ref('stock.stock_location_inter_wh', raise_if_not_found=False)
        if not src_location:
            raise ValidationError(_('Could not find transit location for the company: %s.') % self.company_id.name)
        return {
            'name': _('Voucher Receipt'),
            'sequence_code': 'VR',
            'code': 'internal',
            'sequence_id': self.env['ir.sequence'].search([('code','=', 'picking.type.receipt.voucher'), ('company_id', '=', self.company_id.id)], limit=1).id,
            'warehouse_id': self.id,
            'use_create_lots': True,
            'default_location_src_id': src_location.id,
            'default_location_dest_id': self.lot_stock_id.id,
            'company_id': self.company_id.id
            }

    @api.model
    def _create_voucher_receipt_picking_type(self):
        """
        Create the promotion voucher receipt picking type for the warehouse and assign it to the warehouse

        @return: the newly created picking type
        @rtype: 'stock.picking.type' record
        """
        PickingType = self.env['stock.picking.type']
        picking_type_id = PickingType.create(self._prepare_voucher_receipt_picking_type())
        self.write({
            'voucher_receipt_picking_type_id': picking_type_id.id
            })
        return picking_type_id

    def _create_if_not_exist_voucher_receipt_picking_types(self):
        PickingType = self.env['stock.picking.type']
        Location = self.env['stock.location']
        sequences = self.env['ir.sequence'].search([('code','=', 'picking.type.receipt.voucher')])
        for r in self.filtered(lambda wh: not wh.voucher_receipt_picking_type_id):
            sequence_id = sequences.filtered(lambda sequence: sequence.company_id == r.company_id)[0]
            picking_type_id = PickingType.search([
                ('sequence_id', '=', sequence_id.id),
                ('warehouse_id', '=', r.id),
                ('name', '=', _('Voucher Receipt'))], limit=1)
            if not picking_type_id:
                picking_type_id = PickingType.search([
                ('sequence_id', '=', sequence_id.id),
                ('warehouse_id', '=', r.id)], limit=1)
            if not picking_type_id:
                picking_type_id = PickingType.search([
                ('sequence_id', '=', sequence_id.id),
                ('warehouse_id', '=', False)], limit=1)
            if picking_type_id:
                src_location = Location.search([('usage', '=', 'transit'), ('company_id', '=', r.company_id.id)], limit=1)
                if not src_location:
                    raise ValidationError(_('Could not find transit location for the company: %s.') % r.company_id.name)
                picking_type_id.write({
                    'warehouse_id': r.id,
                    'name': _('Voucher Receipt'),
                    'default_location_src_id': src_location.id,
                    'default_location_dest_id': r.lot_stock_id.id,
                    'company_id': r.company_id.id
                    })
                r.write({
                    'voucher_receipt_picking_type_id': picking_type_id.id
                    })
            else:
                r._create_voucher_receipt_picking_type()

    @api.model
    def create(self, vals):
        res = super(StockWarehouse, self).create(vals)
        res._create_voucher_receipt_picking_type()
        return res

    @api.model
    def prepare_warhouse_data(self):
        """
        To be used during installation/upgrading
        """
        all_warehouses = self.with_context(active_test=False).search([])
        all_warehouses._create_if_not_exist_voucher_receipt_picking_types()

