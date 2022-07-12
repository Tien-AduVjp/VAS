from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero

class RepairLine(models.Model):
    _inherit = 'repair.line'

    stock_move_ids = fields.One2many('stock.move', 'repair_line_id', string='Moves')
    src_location_id = fields.Many2one('stock.location', string='Current Location')
    # the location_id was the source location in the repair module
    # we now turn it into repair location to have moves generated
    # from the src_location_id to this location_id
    location_id = fields.Many2one(string='Repair Location')
    create_picking = fields.Boolean('Create Picking?')
    supply_stock_move_id = fields.Many2one('stock.move', string='Latest Supply Stock Move', copy=False)
    supply_stock_move_ids = fields.Many2many('stock.move', string='Supply Stock Moves', copy=False)

    reserved_completion_stock_move_id = fields.Many2one('stock.move', string='Reserved Completion Stock Move', copy=False)
    consumed_stock_move_ids = fields.One2many('stock.move', string='Consumed Stock Moves', compute='_compute_consumed_stock_moves')
    consumed_qty = fields.Float(string='Consumed Quantity', compute='_compute_consumed_stock_moves', digits='Product Unit of Measure')

    @api.depends('stock_move_ids')
    def _compute_consumed_stock_moves(self):
        for r in self:
            r.consumed_stock_move_ids = r.stock_move_ids.filtered_domain([
                ('location_id', 'child_of', r.location_id.id),
                ('location_dest_id', '=', r.location_dest_id.id)
            ])
            consumed_qty = sum(r.consumed_stock_move_ids.filtered(lambda m: m.state == 'done').mapped('product_qty'))
            r.consumed_qty = r.product_id.uom_id._compute_quantity(consumed_qty, r.product_uom, rounding_method='HALF-UP')

    @api.onchange('type', 'repair_id')
    def onchange_operation_type(self):
        super(RepairLine, self).onchange_operation_type()
        if self.type == 'add':
            self.location_id = self.repair_id.location_id

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if self.lot_id:
            quants = self.lot_id.mapped('quant_ids').filtered(lambda x: x.quantity > 0 and x.location_id.usage == 'internal')
            if quants:
                src_location = quants[0].location_id
                if src_location != self.location_id:
                    self.src_location_id = src_location
            if self.product_id.tracking == 'serial':
                self.product_uom_qty = 1

    @api.constrains('product_id', 'lot_id', 'product_uom_qty')
    def _constraint_product_lot(self):
        for r in self:
            if r.lot_id and r.product_id.tracking == 'serial' and r.product_uom_qty > 1:
                raise ValidationError(_(' A serial number should only be linked to a single product.'))

    def write(self, values):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for r in self.filtered(lambda line: line.type == 'add'):
            if r.supply_stock_move_id or r.consumed_qty:
                checked_keywords = self._not_allowed_edit_field_after_consumption()
                if self._check_vals_contains_keywords(values, checked_keywords):
                    raise UserError(_("You can not change type/product/lot/location/destination location of part, "
                                      "which already been supplying or had consumed quantity."))
                product_uom_qty = values.get('product_uom_qty', False)
                if product_uom_qty:
                    if float_compare(product_uom_qty, r.consumed_qty, precision_digits=precision) < 0:
                        raise UserError(_("Quantity must be greater or equals to consumed quantity."))
        return super(RepairLine, self).write(values)

    def unlink(self):
        for r in self.filtered(lambda line: line.type == 'add'):
            if r.supply_stock_move_id or r.consumed_qty:
                raise UserError(_("You can not delete an operation line, which already been supplying"
                                  " or had consumed quantity. You should set the quantity to 0 instead."))
        return super(RepairLine, self).unlink()

    def _not_allowed_edit_field_after_consumption(self):
        return ['type', 'product_id', 'lot_id', 'location_id', 'location_dest_id']

    def _check_vals_contains_keywords(self, vals, keywords):
        return any(f in vals.keys() for f in keywords)

    def _prepare_stock_move_data(self, picking_id, qty=None):
        if qty is None:
            qty = self.product_uom_qty - self.consumed_qty
        return {
            'name': _('Repair Supply for %s') % self.repair_id.name,
            'date': fields.Datetime.now(),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': qty,
            'location_id': picking_id.location_id.id,
            'location_dest_id': picking_id.location_dest_id.id,
            'company_id': self.env.company.id,
            'origin': self.repair_id.name,
            'repair_line_id': self.id,
            'repair_id': self.repair_id.id,
            'picking_type_id': picking_id.picking_type_id.id,
            'picking_id': picking_id.id,
            'group_id': self.repair_id.group_id.id,
            }

    def _prepare_completion_stock_move_data(self, qty):
        move_orig_ids = self.repair_id.move_ids.filtered_domain([
            ('product_id', '=', self.product_id.id),
            ('location_id', 'child_of', self.src_location_id.ids),
            ('location_dest_id', '=', self.location_id.id),
            ])
        return {
            'name': self.repair_id.name,
            'date': fields.Datetime.now(),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': qty,
            'partner_id': self.repair_id.address_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.env.company.id,
            'origin': self.repair_id.name,
            'repair_line_id': self.id,
            'repair_id': self.repair_id.id,
            'group_id': self.repair_id.group_id.id,
            'move_orig_ids': [(6, 0, move_orig_ids.ids)],
        }

    def _generate_moves(self, picking_id, qty=None):
        if not picking_id:
            return
        for r in self:
            move = self.env['stock.move'].create(r._prepare_stock_move_data(picking_id, qty))
            # By default, when we confirm stock move, merge parameter is True,
            # it mean this move will be merged into another move, which shares same characteristics.
            # But in this module, we need to keep separate supply stock move for each repair line, so we set merge parameter is False
            move._action_confirm(merge=False)
            move._action_assign()
            if r.lot_id:
                move.move_line_ids.write({'lot_id': r.lot_id.id})
            r.write({
                'supply_stock_move_id': move.id,
                'supply_stock_move_ids': [(4, move.id)],
                })
            if r.reserved_completion_stock_move_id and r.reserved_completion_stock_move_id.state not in ('done', 'cancel'):
                move.write({'move_dest_ids': [(4, r.reserved_completion_stock_move_id.id)]})
        return True

    def _generate_completion_moves(self, qty):
        self.ensure_one()
        move = self.env['stock.move'].create(self._prepare_completion_stock_move_data(qty))
        move._action_confirm(merge=False)
        move._action_assign()
        # Best effort to reserve the product in a (sub)-location where it is available
        product_qty = move.product_uom._compute_quantity(
            qty, move.product_id.uom_id, rounding_method='HALF-UP')
        available_quantity = self.env['stock.quant']._get_available_quantity(
            move.product_id,
            move.location_id,
            lot_id=self.lot_id,
            strict=False,
        )
        if move.product_id.tracking != 'serial':
            move._update_reserved_quantity(
                product_qty,
                available_quantity,
                move.location_id,
                lot_id=self.lot_id,
                strict=False,
            )
        return move

    def _action_prepare_done_for_completion_moves(self, move):
        self.ensure_one()
        move._set_quantity_done(move.product_uom_qty)

        if self.lot_id:
            move.move_line_ids.write({'lot_id': self.lot_id.id})

    def _generate_reserved_completion_moves(self):
        assigned_moves = self.env['stock.move']
        partially_available_moves = self.env['stock.move']
        for r in self:
            move = r._generate_completion_moves(r.product_uom_qty - r.consumed_qty)
            r.reserved_completion_stock_move_id = move
            if float_is_zero(move.reserved_availability, precision_rounding=move.product_uom.rounding):
                continue
            elif float_compare(move.reserved_availability, move.product_uom_qty, precision_rounding=move.product_uom.rounding) < 0:
                partially_available_moves |= move
            else:
                assigned_moves |= move
        assigned_moves.write({'state': 'assigned'})
        partially_available_moves.write({'state': 'partially_available'})

    def _generate_product_pickings(self):
        # we don't want to generate pickings for operation that are not 'add' or not require picking created
        lines_to_create_picking = self.filtered(lambda x: x.create_picking and x.type == 'add' and x.product_id.type in ('consu', 'product'))

        pickings = self.env['stock.picking']
        for repair in lines_to_create_picking.mapped('repair_id'):
            # all lines of a repair have the same repair location (location_id)
            # since the field is a related field to the repair's location
            # we just need to loop for different source locations to create picking for each
            for source_localtion in lines_to_create_picking.filtered(lambda l: l.repair_id == repair).mapped('src_location_id'):
                picking = pickings.create(repair._prepare_stock_picking_data(source_localtion))
                lines = lines_to_create_picking.filtered(lambda l: l.src_location_id == source_localtion and l.repair_id == repair)
                lines._generate_moves(picking)
                pickings += picking
        return pickings

    def _prepare_return_stock_move_data(self, return_qty):
        self.ensure_one()
        supply_move = self.supply_stock_move_id
        return {
            'name': _('Return for repair order %s') % self.repair_id.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': return_qty,
            'partner_id': self.repair_id.address_id.id,
            'location_id': supply_move.location_dest_id.id,
            'location_dest_id': supply_move.location_id.id,
            'repair_line_id': self.id,
            'repair_id': self.repair_id.id,
            'company_id': self.env.company.id,
            'origin': self.repair_id.name,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom.id,
                'location_id': supply_move.location_dest_id.id,
                'location_dest_id': supply_move.location_id._get_putaway_strategy(self.product_id).id or supply_move.location_id.id,
                'lot_id': self.lot_id.id,
                'qty_done': return_qty,
            })],
            }

    def _return_remaining_supplies(self):
        # Return remaining supplied products and cancel the pending move
        self.ensure_one()
        done_supply_moves = self.supply_stock_move_ids.filtered(lambda m: m.state == 'done')
        if done_supply_moves:
            supplied_qty = sum(done_supply_moves.mapped('product_qty'))
            return_qty = self.product_id.uom_id._compute_quantity(supplied_qty, self.product_uom, rounding_method='HALF-UP') - self.consumed_qty
            if not float_is_zero(return_qty, precision_rounding=self.product_uom.rounding):
                return_move_data = self._prepare_return_stock_move_data(return_qty)
                return_move = self.env['stock.move'].create(return_move_data)
                return_move._action_done()

    def action_cancel(self):
        for r in self:
            # Cancel reserved stock move at first
            if r.reserved_completion_stock_move_id.state != 'done':
                r.reserved_completion_stock_move_id._action_cancel()
            # Then, return back what've been supplied to source location
            if r.src_location_id:
                r._return_remaining_supplies()
                if r.supply_stock_move_id.state not in ['done','cancel']:
                    r.supply_stock_move_id._action_cancel()
            r.supply_stock_move_id = False
            r.reserved_completion_stock_move_id = False
