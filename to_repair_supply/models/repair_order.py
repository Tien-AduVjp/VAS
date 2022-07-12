from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class Repair(models.Model):
    _inherit = 'repair.order'

    group_id = fields.Many2one('procurement.group', string='Procurement Group', copy=False,
                               help="This procurement group is used for auto-reserving between stock moves, "
                                    "eg: When a supplying stock move for a part is validated, the "
                                    "next reserving stock move for that part at repair location should "
                                    "be reserved automatically.")
    picking_ids = fields.One2many('stock.picking', 'repair_id', string=' Stock Pickings')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')
    state = fields.Selection(selection_add=[('delivered', 'Delivered')],
        help="* The \'Draft\' status is used when a user is encoding a new and unconfirmed repair order.\n"
             "* The \'Confirmed\' status is used when a user confirms the repair order.\n"
             "* The \'Ready to Repair\' status is used to start to repairing, user can start repairing only after repair order is confirmed.\n"
             "* The \'To be Invoiced\' status is used to generate the invoice before or after repairing done.\n"
             "* The \'Done\' status is set when repairing is completed.\n"
             "* The \'Delivered\' status is used when the repaired product is delivered back to source location from repair location.\n"
             "* The \'Cancelled\' status is used when user cancel repair order.")
    move_ids = fields.One2many('stock.move', 'repair_id', string='Product Stock Moves')
    move_count = fields.Integer(string='Product Moves Count', compute='_compute_move_count')
    supply_stock_move_id = fields.Many2one('stock.move', string='Latest Supply Stock Move', copy=False)
    reserved_completion_stock_move_id = fields.Many2one('stock.move', string='Reserved Completion Stock Move', copy=False)

    def _prepare_return_stock_move_data(self, src_move):
        return {
            'name': _('Repair Delivery for %s') % self.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id or self.product_id.uom_id.id,
            'product_uom_qty': self.product_qty,
            'partner_id': self.address_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': src_move.location_id.id,
            'repair_id': self.id,
            'origin': self.name,
            }

    def action_delivery_confirm(self):
        Move = self.env['stock.move']
        for repair in self:
            if repair.state != 'done':
                raise ValidationError(_("Repair must be done before delivery confirm."))
            src_move = self.env['stock.move'].search([
                ('product_id', '=', repair.product_id.id),
                ('location_dest_id', '=', repair.location_id.id),
                ('repair_id', '=', repair.id),
                ('state', '=', 'done'),
                ('id', '!=', repair.move_id.id),
            ], limit=1)
            if src_move:
                return_move_data = repair._prepare_return_stock_move_data(src_move)
                move = Move.create(return_move_data)
                move._action_confirm()
                move._action_assign()
                if move.repair_id and move.repair_id.product_id.tracking == 'serial' and move.repair_id.lot_id:
                    move.move_line_ids.write({'lot_id': move.repair_id.lot_id.id, 'qty_done': 1.0})
                else:
                    for move_line in move.move_line_ids:
                        move_line.write({'lot_id': move.repair_id.lot_id.id, 'qty_done': move_line.product_uom_qty})
                move._action_done()
            self.supply_stock_move_id = False
            repair.write({'state': 'delivered'})
        return

    @api.constrains('product_id', 'lot_id', 'product_qty')
    def _constraint_product_lot(self):
        for r in self:
            if r.lot_id and r.product_id.tracking == 'serial' and r.product_qty > 1:
                raise ValidationError(_(" A serial number should only be linked to a single product."))

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for r in self:
            r.delivery_count = len(r.picking_ids)

    @api.depends('move_ids')
    def _compute_move_count(self):
        for r in self:
            r.move_count = len(r.move_ids)

    def action_view_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given repair order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action

    def action_view_product_move(self):
        '''
        This function returns an action that display existing product stock moves
        of given repair order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('stock.stock_move_action')
        result = action.read()[0]
        result['context'] = {}
        moves = self.mapped('move_ids')
        if len(moves) > 1:
            result['domain'] = [('id', 'in', moves.ids)]
        elif moves:
            result['views'] = [(self.env.ref('stock.view_move_form').id, 'form')]
            result['res_id'] = moves.id
        return result

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if self.lot_id:
            quants = self.lot_id.mapped('quant_ids').filtered(lambda x: x.quantity > 0)
            if quants:
                self.location_id = quants[0].location_id
            if self.product_id.tracking == 'serial':
                self.product_qty = 1

    @api.onchange('location_id')
    def onchange_location_id(self):
        for line in self.operations:
            if line.type == 'add':
                line.location_id = self.location_id

    def action_validate(self):
        self.ensure_one()
        for line in self.operations.filtered(lambda op: op.type == 'add'):
            # Check if location of repair line is not consistent with location of repair order
            if line.location_id != self.location_id:
                raise ValidationError(_("The product %s in %s is not consistent with location of repair order.")
                                      % (line.product_id.display_name, line.location_id.display_name))
                
            if line.src_location_id == line.location_id:
                raise ValidationError(_("The product %s has repair location in %s. "
                                        "So you could not select current location same with this location.")
                                      % (line.product_id.display_name, line.location_id.display_name))
                
            if line.location_id.usage == 'customer':
                if line.src_location_id:
                    line.write({'create_picking': True})
            else:
                if line.product_id.type == 'product':
                    precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                    available_qty = self.env['stock.quant']._get_available_quantity(line.product_id, line.location_id, line.lot_id, strict=True)
                    product_qty = line.product_uom._compute_quantity(
                        line.product_uom_qty - line.consumed_qty, line.product_id.uom_id, rounding_method='HALF-UP')
                    # check available qty in repair location
                    # if enough, dont create picking
                    if float_compare(available_qty, product_qty, precision_digits=precision) < 0:
                        if not line.src_location_id:
                            raise ValidationError(_("The product %s is not available in sufficient quantity in %s. "
                                                    "You should select current location of this product in operation line.")
                                                  % (line.product_id.display_name, line.location_id.display_name))
                        else:
                            line.write({'create_picking': True})
                    else:
                        line.write({'create_picking': False})
                else:
                    if line.src_location_id:
                        line.write({'create_picking': True})
                    
        return super(Repair, self).action_validate()

    def _generate_moves(self, src_location_id):
        if not src_location_id.should_bypass_reservation():
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            available_qty = self.env['stock.quant']._get_available_quantity(self.product_id, src_location_id, self.lot_id, strict=False)
            product_qty = self.product_uom._compute_quantity(
                        self.product_qty, self.product_id.uom_id, rounding_method='HALF-UP')
            if float_compare(available_qty, product_qty, precision_digits=precision) < 0:
                raise ValidationError(_("The product %s does not have enough available quantity in %s. "
                                        "You should select another location or provide enough available quantity for this location.")
                                      % (self.product_id.display_name, src_location_id.display_name))
        
        move = self.env['stock.move'].create({
            'name': _('Repair Supply for %s') % self.name,
            'date': fields.Datetime.now(),
            'date_expected': fields.Datetime.now(),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': self.product_qty,
            'location_id': src_location_id.id,
            'location_dest_id': self.location_id.id,
            'company_id': self.company_id.id or self.env.company.id,
            'origin': self.name,
            'repair_id': self.id,
        })
        move._action_confirm()
        move._action_assign()
        if move.repair_id and move.repair_id.product_id.tracking == 'serial' and move.repair_id.lot_id:
            move.move_line_ids.write({'lot_id': move.repair_id.lot_id.id, 'qty_done': 1.0})
        else:
            for move_line in move.move_line_ids:
                move_line.write({'lot_id': move.repair_id.lot_id.id, 'qty_done': move_line.product_uom_qty})
        move._action_done()
        self.supply_stock_move_id = move.id
        
        return True
    
    def _generate_reserved_completion_move(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        move = self.env['stock.move'].create(self._prepare_reserved_completion_stock_move_data())
        move._action_confirm()
        product_qty = move.product_uom._compute_quantity(
            self.product_qty, move.product_id.uom_id, rounding_method='HALF-UP')
        # Try to create move with the appropriate owner
        owner_id = False
        available_qty_owner = self.env['stock.quant']._get_available_quantity(self.product_id, self.location_id, self.lot_id, owner_id=self.partner_id, strict=True)
        if float_compare(available_qty_owner, product_qty, precision_digits=precision) >= 0:
            owner_id = self.partner_id.id
        if self.product_id.type == 'product':
            available_quantity = self.env['stock.quant']._get_available_quantity(
                move.product_id,
                move.location_id,
                lot_id=self.lot_id,
                strict=False,
            )
            move._update_reserved_quantity(
                product_qty,
                available_quantity,
                move.location_id,
                lot_id=self.lot_id,
                strict=False,
                owner_id=owner_id
            )
            move.write({'state': 'assigned'})
        else:
            move._action_assign()
        self.reserved_completion_stock_move_id = move

    def _prepare_stock_picking_data(self, src_location):
        self.ensure_one()
        picking_type_id = self.env.ref('to_repair_supply.picking_type_repair_supply')
        return {
            'location_id': src_location.id,
            'location_dest_id': self.location_id.id,
            'scheduled_date': fields.Datetime.now(),
            'picking_type_id': picking_type_id.id,
            'repair_id': self.id,
            'origin': self.name,
            'group_id': self.group_id.id,
            'company_id': self.company_id.id or self.env.company.id,
            }

    def _prepare_procurement_group_vals(self):
        self.ensure_one()
        return {
            'name': self.name,
            'partner_id': self.partner_id.id,
        }
        
    def _generate_procurement_group(self):
        if not self.group_id:
            vals = self._prepare_procurement_group_vals()
            self.write({'group_id': self.env['procurement.group'].create(vals)})

    def action_repair_confirm(self):
        for r in self:
            # Create reserved stock moves for repaired product right after confirm repair order
            r._generate_reserved_completion_move()
            # Create procurement group for auto-reserving process when moving parts
            # from Source Location => Repair Location => Destination Location
            r._generate_procurement_group()
            # Create supply picking
            r.operations._generate_product_pickings()
            # Create reserved stock moves for repair lines with type is 'add' from repair location to destination location
            # These stock moves will support to calculate reserved quantity of products in repair location correctly
            r.operations.filtered(lambda op: op.type == 'add' and op.product_id.type != 'service')._generate_reserved_completion_moves()
        
        return super(Repair, self).action_repair_confirm()

    def action_repair_start(self):
        for r in self:
            if r.picking_ids.filtered(lambda x: x.state not in ['done', 'cancel']):
                raise ValidationError(_("Some stock pickings related to this repair order were not validated. "
                                        "Please validate them before you can start this order."))
            
            # Check if the reserving stock moves have been fully reserved
            for operation in r.operations.filtered(lambda op: op.type == 'add' and op.product_id.type == 'product'):
                if not operation.location_id.should_bypass_reservation():
                    if operation.reserved_completion_stock_move_id.state != 'assigned':
                        raise ValidationError(_("The product %s has not been reserved enough quantity in %s. "
                                                "You must supply enough product quantity to start the process.")
                                              % (operation.product_id.display_name, operation.location_id.display_name))
        
        res = super(Repair, self).action_repair_start()
        
        return res

    def action_repair_cancel(self):
        for repair in self:
            repair.operations.action_cancel()
            repair.mapped('picking_ids').filtered(lambda x: x.state != 'done').action_cancel()
            if repair.reserved_completion_stock_move_id:
                repair.reserved_completion_stock_move_id._action_cancel()
            
            if repair.supply_stock_move_id:
                return_move_data = repair._prepare_return_stock_move_data(repair.supply_stock_move_id)
                return_move_data['name'] = _('Return for repair order %s') % repair.name
                move = self.env['stock.move'].create(return_move_data)
                move._action_confirm()
                move._action_assign()
                if move.repair_id and move.repair_id.product_id.tracking == 'serial' and move.repair_id.lot_id:
                    move.move_line_ids.write({'lot_id': move.repair_id.lot_id.id, 'qty_done': 1.0})
                else:
                    for move_line in move.move_line_ids:
                        move_line.write({'lot_id': move.repair_id.lot_id.id, 'qty_done': move_line.product_uom_qty})
                move._action_done()
                repair.supply_stock_move_id = False
        return super(Repair, self).action_repair_cancel()
    
    def action_repair_end(self):
        if self._context.get('check_consumption', False):
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            # check if repair has remaining parts which is not consumed
            remaining_operations = self.mapped('operations').filtered(lambda op: op.type == 'add'
                                                            and float_compare(op.product_uom_qty, op.consumed_qty, precision_digits=precision) > 0)
            if remaining_operations:
                view = self.env.ref('to_repair_supply.wizard_repair_order_confirm_consumption_view_form')
                wiz = self.env['wizard.repair.order.confirm.consumption'].create({'repair_id': self.id})
                return {
                    'name': _('Confirm Create Consumption'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'wizard.repair.order.confirm.consumption',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id
                }
        return super(Repair, self).action_repair_end()
    
    def action_repair_done(self):
        """ 
        Overwrite method of repair module to handle reserved completion stock moves
        """
        if self.filtered(lambda repair: not repair.repaired):
            raise UserError(_("Repair must be repaired in order to make the product moves."))
        res = {}
        without_consumption = self._context.get('without_consumption', False)

        for r in self:
            moves_to_done = self.env['stock.move']
            consumed_moves = self.env['stock.move']
            consuming_moves_to_done = self.env['stock.move']
            for operation in r.operations:
                if operation.type == 'add':
                    done_consumed_stock_moves = operation.consumed_stock_move_ids.filtered(lambda m: m.state == 'done')
                    # Check if repair line didn't consume before, we will complete reserved completion stock move of this line
                    if operation.reserved_completion_stock_move_id.state != 'done':
                        if not without_consumption:
                            operation._action_prepare_done_for_completion_moves(operation.reserved_completion_stock_move_id)
                            consuming_moves_to_done |= operation.reserved_completion_stock_move_id
                            operation.write({'move_id': operation.reserved_completion_stock_move_id.id, 'state': 'done'})
                        else:
                            # cancel reserved stock move
                            operation.reserved_completion_stock_move_id._action_cancel()
                            # return the remaining parts to source location, if source location is specified
                            if operation.src_location_id:
                                operation._return_remaining_supplies()
                            if done_consumed_stock_moves:
                                operation.write({'move_id': done_consumed_stock_moves[0].id, 'state': 'done'})
                            else:
                                operation.write({'state': 'done'})
                                
                    consumed_moves |= done_consumed_stock_moves
                else:
                    # For remove product
                    move = operation._generate_completion_moves(operation.product_uom_qty)
    
                    operation._action_prepare_done_for_completion_moves(move)
    
                    consuming_moves_to_done |= move
                    
                    operation.write({'move_id': move.id, 'state': 'done'})
            
            consumed_moves |= consuming_moves_to_done
            
            r.reserved_completion_stock_move_id.move_line_ids[0].write({'qty_done': r.product_qty})
            
            consumed_lines = consumed_moves.mapped('move_line_ids')
            produced_lines = r.reserved_completion_stock_move_id.move_line_ids
            moves_to_done |= r.reserved_completion_stock_move_id
            moves_to_done |= consuming_moves_to_done
            moves_to_done._action_done()
            produced_lines.write({'consume_line_ids': [(6, 0, consumed_lines.ids)]})
            res[r.id] = r.reserved_completion_stock_move_id.id
        return res

    def _prepare_reserved_completion_stock_move_data(self):
        return {
            'name': self.name,
            'date': fields.Datetime.now(),
            'date_expected': fields.Datetime.now(),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': self.product_qty,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_id.id,
            'company_id': self.company_id.id or self.env.company.id,
            'origin': self.name,
            'repair_id': self.id
        }
