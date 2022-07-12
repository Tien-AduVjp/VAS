from odoo import models, fields, api


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'


    lot_id = fields.Many2one('stock.production.lot',
                             string="Logistics Serial Number", tracking=True,
                             help='The unique logistics serial number that associated with the Equipment')
    created_from_stock_lot = fields.Boolean(string='Created from Stock Lot', readonly=True, default=False)

    product_id = fields.Many2one('product.product',
                                 string='Associated Product', related='lot_id.product_id', store=True, index=True, readonly=True)

    serial_no = fields.Char(compute='_compute_serial_no', inverse='_inverse_serial_no', store=True, tracking=True)

    current_stock_location_id = fields.Many2one('stock.location', string='Current Stock Location', tracking=True,
                                                compute='_compute_current_stock_location_id', store=True)


    stock_move_lines = fields.One2many('stock.move.line', 'equipment_id', string='Move History')
    history_count = fields.Integer(string='Move History Count', compute='_compute_history_count', compute_sudo=True, store=True)


    @api.depends('stock_move_lines')
    def _compute_history_count(self):
        for r in self:
            r.history_count = len(r.stock_move_lines)

    @api.depends('lot_id')
    def _compute_serial_no(self):
        for r in self:
            if r.lot_id and not r.serial_no:
                r.serial_no = r.lot_id.name
            else:
                r.serial_no = r._origin.serial_no or r.serial_no

    def _inverse_serial_no(self):
        pass

    @api.depends('lot_id', 'lot_id.quant_ids.quantity')
    def _compute_current_stock_location_id(self):
        for r in self:
            r.current_stock_location_id = False
            if r.lot_id:
                quants = r.lot_id.quant_ids.filtered(lambda x: x.quantity > 0)
                if quants:
                    r.current_stock_location_id = quants[0].location_id
