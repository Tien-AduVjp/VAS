from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError


class WizardRepairRequestSupply(models.TransientModel):
    _name = 'wizard.repair.request.supply'
    _description = 'Repair Request Supply Wizard'

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
    location_id = fields.Many2one('stock.location', related='order_id.location_id')
    line_ids = fields.One2many('wizard.repair.request.supply.line', 'wizard_id', string='Repair Lines')

    def action_request(self):
        """ Generate supplying stock transfers and update to repair lines.
            If there is a repair line that suit any supplying line (which has
            the same product and same locations settings), update the quantity
            on that repair line, otherwise create a new one.
        """
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("You have to add some products to request supply."))
        self.line_ids._do_supply()


class WizardRepairRequestSupplyLine(models.TransientModel):
    _name = 'wizard.repair.request.supply.line'
    _description = 'Repair Request Supply Line Wizard'

    wizard_id = fields.Many2one('wizard.repair.request.supply', string='Repair Request Supply Wizard', required=True, ondelete='cascade')
    order_id = fields.Many2one('repair.order', string='Repair Order', related='wizard_id.order_id')
    repair_line_id = fields.Many2one('repair.line', string='Repair Line')
    product_id = fields.Many2one('product.product', string='Product', required=True, domain=[('type', 'in', ['product','consu'])])
    name = fields.Text(string='Description', required=True)
    lot_id = fields.Many2one('stock.production.lot', string='Lot/Serial', domain="[('product_id', '=', product_id)]")
    src_location_id = fields.Many2one('stock.location', string='Current Location')
    location_id = fields.Many2one('stock.location', 'Source Location', required=True)
    location_dest_id = fields.Many2one('stock.location', 'Dest. Location', required=True)
    product_uom_qty = fields.Float('Request Qty', default=1.0, digits='Product Unit of Measure', required=True)
    product_uom = fields.Many2one('uom.uom', 'UoM', required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        repair = self.order_id
        partner = repair.partner_id
        # Fill default description and UoM
        if not self.product_id or not self.product_uom_qty:
            return
        if self.product_id:
            if partner:
                self.name = self.product_id.with_context(lang=partner.lang).display_name
            else:
                self.name = self.product_id.display_name
            if self.product_id.description_sale:
                if partner:
                    self.name += '\n' + self.product_id.with_context(lang=partner.lang).description_sale
                else:
                    self.name += '\n' + self.product_id.description_sale
            self.product_uom = self.product_id.uom_id.id
        # Assign default locations
        self.location_id = repair.location_id
        self.location_dest_id = self.env['stock.location'].search([('usage', '=', 'production')], limit=1).id

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

    def _prepair_repair_line_vals(self):
        self.ensure_one()
        partner = self.order_id.partner_id
        # Get the price unit
        price = 0.0
        pricelist = self.order_id.pricelist_id
        if pricelist:
            price = pricelist.get_product_price(self.product_id, self.product_uom_qty, partner, uom_id=self.product_uom.id)
        # Get the taxes
        fp = partner.property_account_position_id
        if not fp:
            fp_id = self.env['account.fiscal.position'].get_fiscal_position(partner.id, delivery_id=self.order_id.address_id.id)
            fp = self.env['account.fiscal.position'].browse(fp_id)
        taxes = self.product_id.taxes_id.filtered(lambda x: x.company_id == self.order_id.company_id)
        tax_ids = fp.map_tax(taxes, self.product_id, partner).ids

        return {
            'repair_id': self.order_id.id,
            'type': 'add',
            'product_id': self.product_id.id,
            'name': self.name,
            'lot_id': self.lot_id.id,
            'src_location_id': self.src_location_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': self.product_uom.id,
            'price_unit': price,
            'tax_id': [(6, 0, tax_ids)],
            }

    def _create_repair_line(self):
        vals = self._prepair_repair_line_vals()
        return self.env['repair.line'].create(vals)

    def _update_repair_line(self):
        """ Find an existing suitable repair line and add the requesting quantity to it.
            If could not find any lines, create a new one with the requesting quantity.
        """
        self.ensure_one()
        repair_line = self.order_id.operations.filtered(
            lambda l: l.type == 'add' and \
                      l.product_id == self.product_id and \
                      l.src_location_id == self.src_location_id and \
                      l.location_id == self.location_id and \
                      l.location_dest_id == self.location_dest_id)[:1]
        if repair_line:
            request_qty = self.product_uom._compute_quantity(self.product_uom_qty, repair_line.product_uom, rounding_method='HALF-UP')
            repair_line.write({
                'product_uom_qty': repair_line.product_uom_qty + request_qty
                })
        else:
            repair_line = self._create_repair_line()
        self.repair_line_id = repair_line

    def _update_supply_stock_move(self):
        self.ensure_one()
        repair_line = self.repair_line_id
        supply_move = repair_line.supply_stock_move_id
        if supply_move:
            request_uom_qty = self.product_uom._compute_quantity(self.product_uom_qty, supply_move.product_uom, rounding_method='HALF-UP')
        else:
            request_uom_qty = self.product_uom._compute_quantity(self.product_uom_qty, repair_line.product_uom, rounding_method='HALF-UP')
        request_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id, rounding_method='HALF-UP')
        if supply_move and supply_move.state not in ('done','cancel'):
            # If there is a pending supply move, we'll update the quantity on that move and do reservation
            supply_move.write({
                'product_uom_qty': supply_move.product_uom_qty + request_uom_qty
                })
            available_quantity = self.env['stock.quant']._get_available_quantity(
                supply_move.product_id,
                supply_move.location_id,
                lot_id=self.lot_id,
                strict=False,
            )
            supply_move._update_reserved_quantity(
                request_qty,
                available_quantity,
                supply_move.location_id,
                lot_id=self.lot_id,
                strict=False,
            )
        else:
            # If there is no pending supply move, we'll generate a new one
            picking = self.order_id.picking_ids.filtered(
                lambda p: p.location_id == self.src_location_id \
                          and p.location_dest_id == self.location_id \
                          and p.state not in ['done','cancel'])[:1]
            if not picking:
                picking = self.env['stock.picking'].create(self.order_id._prepare_stock_picking_data(self.src_location_id))
            supply_move = repair_line._generate_moves(picking, qty=request_uom_qty)
        return supply_move

    def _update_reserve_stock_move(self):
        self.ensure_one()
        repair_line = self.repair_line_id
        request_uom_qty = self.product_uom._compute_quantity(self.product_uom_qty, repair_line.product_uom, rounding_method='HALF-UP')
        request_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id, rounding_method='HALF-UP')
        available_qty = self.env['stock.quant']._get_available_quantity(
            repair_line.product_id,
            repair_line.location_id,
            lot_id=repair_line.lot_id,
            strict=False,
        )
        # If no source location specified, we'll have to check if the request quantity
        # is greater than the available quantity in current repair location
        if not self.src_location_id:
            if float_compare(request_qty, available_qty, precision_rounding=self.product_id.uom_id.rounding) > 0:
                raise UserError(_("The requesting quantity for product %s is greater than the available quantity in %s. "
                                  "Please specify a source location to request supply.") \
                                  % (self.product_id.display_name, self.location_id.complete_name))

        reserve_move = repair_line.reserved_completion_stock_move_id
        if reserve_move and reserve_move.state not in ('done', 'cancel'):
            # Do the reservation
            reserve_move.write({
                'product_uom_qty': reserve_move.product_uom_qty + request_uom_qty
                })
            reserve_move._update_reserved_quantity(
                request_qty,
                available_qty,
                reserve_move.location_id,
                lot_id=self.lot_id,
                strict=False,
            )
        else:
            reserve_move = repair_line._generate_completion_moves(request_uom_qty)
            if not float_is_zero(reserve_move.reserved_availability, precision_rounding=reserve_move.product_uom.rounding):
                if float_compare(reserve_move.reserved_availability, reserve_move.product_uom_qty, precision_rounding=reserve_move.product_uom.rounding) < 0:
                    reserve_move.write({'state': 'partially_available'})
                else:
                    reserve_move.write({'state': 'assigned'})
            repair_line.reserved_completion_stock_move_id = reserve_move.id
        return reserve_move

    def _do_supply(self):
        for r in self:
            r._update_repair_line()
            if self.src_location_id:
                r._update_supply_stock_move()
            r._update_reserve_stock_move()
