from odoo import models, fields, _, api
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError

class WizardRepairOrderConsumption(models.TransientModel):
    _name = 'wizard.repair.order.consumption'
    _description = 'Repair Order Consumption Wizard'

    def _default_repair_order(self):
        order_id = False
        if self._context.get('active_model') == 'repair.order':
            order_id = self._context.get('active_id')
        if not order_id:
            params = self._context.get('params', {})
            if params.get('model') == 'repair.order':
                order_id = params.get('id')
        if not order_id:
            return self.env['repair.order']
        return self.env['repair.order'].browse(order_id)

    order_id = fields.Many2one('repair.order', string='Repair Order', required=True, ondelete='cascade', default=_default_repair_order, readonly=True)
    name = fields.Char(string='Repair Order Reference', related='order_id.name')
    line_ids = fields.One2many('wizard.repair.line.consumption', 'wizard_id', string='Repair Lines', compute='_compute_info', readonly=False, store=True)
    show_warning_update_quantity = fields.Boolean(string='Show Warning Update Quantity', compute='_compute_show_warning_update_quantity')

    @api.depends('order_id')
    def _compute_info(self):
        for r in self:
            if r.order_id:
                line_ids = self.env['wizard.repair.line.consumption']
                order_lines = r.order_id.operations.filtered(lambda line: line.type == 'add')

                for line in order_lines:
                    new_line = line_ids.new(r._prepare_wizard_repair_line_consumption_data(line))
                    line_ids += new_line

                r.line_ids = line_ids

    @api.depends('line_ids')
    def _compute_show_warning_update_quantity(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for r in self:
            r.show_warning_update_quantity = False
            for line in r.line_ids:
                if float_compare(line.request_qty + line.consumed_qty, line.product_uom_qty, precision_digits=precision) > 0:
                    r.show_warning_update_quantity = True
                    break

    def action_consume(self):
        self.ensure_one()
        if not any(self.line_ids.mapped('request_qty')):
            raise UserError(_("You didn't request any consumption."))

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        moves = self.env['stock.move']

        # Check consumption request of each repair line to create consumed stock moves
        for line in self.line_ids:
            if float_is_zero(line.request_qty, precision_digits=precision):
                continue
            ori_repair_line = line.repair_line_id
            reserved_move = ori_repair_line.reserved_completion_stock_move_id
            consuming_qty = ori_repair_line.consumed_qty + line.request_qty

            if line.product_id.type == 'product' and not reserved_move.location_id.should_bypass_reservation():
                # check available quantity of product in repair location
                available_qty = self.env['stock.quant']._get_available_quantity(
                    reserved_move.product_id,
                    reserved_move.location_id,
                    lot_id=ori_repair_line.lot_id,
                    strict=False,
                )

                request_product_qty = reserved_move.product_uom._compute_quantity(
                    line.request_qty, reserved_move.product_id.uom_id, rounding_method='HALF-UP')

                # check available quantity based reserved stock move
                # if reserved stock move is not done, we only check available quantity when request quantity is greater than reserved quantity
                # else we always check available quantity before consuming
                if reserved_move.state != 'done':
                    reserved_qty = reserved_move.reserved_availability
                    if float_compare(reserved_qty, request_product_qty, precision_digits=precision) < 0:
                        if float_compare(available_qty, line.request_qty - reserved_qty, precision_digits=precision) < 0:
                            raise ValidationError(_("The product %s does not have enough available quantity in %s. "
                                                    "You must supply enough product quantity for this location.")
                                                  % (reserved_move.product_id.display_name, reserved_move.location_id.display_name))
                else:
                    if float_compare(available_qty, line.request_qty, precision_digits=precision) < 0:
                        raise ValidationError(_("The product %s does not have enough available quantity in %s. "
                                                "You must supply enough product quantity for this location.")
                                              % (reserved_move.product_id.display_name, reserved_move.location_id.display_name))

            # in case consuming quantity is greater than original quantity
            if float_compare(ori_repair_line.product_uom_qty , consuming_qty, precision_digits=precision) < 0:
                # if reserved stock move is done by previous consumption, create new move
                if reserved_move.state == 'done':
                    move = ori_repair_line._generate_completion_moves(line.request_qty)
                    ori_repair_line._action_prepare_done_for_completion_moves(move)
                    moves |= move
                else:
                    # update quantity for reserved stock move based on request quantity
                    # use reserved stock move to transfer for this consumption
                    self._update_quantity_for_reserved_stock_move(reserved_move, line.request_qty, ori_repair_line.lot_id)
                    ori_repair_line._action_prepare_done_for_completion_moves(reserved_move)
                    moves |= reserved_move

                # if user want to update original quantity when consuming quantity is greater than original, we will update it
                if line.should_update_quantity:
                    ori_repair_line.product_uom_qty = consuming_qty

            else:
                remain_qty = ori_repair_line.product_uom_qty - ori_repair_line.consumed_qty
                if float_compare(line.request_qty, remain_qty, precision_digits=precision) == 0:
                    # User reserved completion stock move of repair line to consume part
                    ori_repair_line._action_prepare_done_for_completion_moves(reserved_move)
                    moves |= reserved_move
                else:
                    # Create new stock move to consume part
                    move = ori_repair_line._generate_completion_moves(line.request_qty)
                    ori_repair_line._action_prepare_done_for_completion_moves(move)
                    moves |= move

                    # Update reserved stock move
                    self._update_quantity_for_reserved_stock_move(reserved_move, remain_qty - line.request_qty, ori_repair_line.lot_id)

        moves._action_done()

    def _update_quantity_for_reserved_stock_move(self, reserved_move, qty, lot_id):
        # Update demand qty and reserved qty of reserved completion stock move
        reserved_move.write({'product_uom_qty': qty})

        product_qty = reserved_move.product_uom._compute_quantity(
            qty, reserved_move.product_id.uom_id, rounding_method='HALF-UP')
        available_quantity = self.env['stock.quant']._get_available_quantity(
            reserved_move.product_id,
            reserved_move.location_id,
            lot_id=lot_id,
            strict=False,
        )
        reserved_move._update_reserved_quantity(
            product_qty,
            available_quantity,
            reserved_move.location_id,
            lot_id=lot_id,
            strict=False,
        )
        reserved_move.write({'state': 'assigned'})

    def _prepare_wizard_repair_line_consumption_data(self, line):
        return {
            'product_id': line.product_id.id,
            'wizard_id': self.id,
            'name': line.name,
            'lot_id': line.lot_id.id,
            'product_uom_qty': line.product_uom_qty,
            'consumed_qty': line.consumed_qty,
            'repair_line_id': line.id,
            'request_qty': max(line.product_uom_qty - line.consumed_qty, 0)
        }
