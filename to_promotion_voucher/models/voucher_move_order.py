from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VoucherMoveOrder(models.Model):
    _name = 'voucher.move.order'
    _description = 'Voucher Move Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'move_date asc,id'

    name = fields.Char(
        'Reference', copy=False, readonly=True, default='/')
    origin = fields.Char(
        'Source', copy=False,
        help="Reference of the document that generated this order request.")

    warehouse_id = fields.Many2one('stock.warehouse', string='Shop / Warehouse', readonly=False, required=True, index=True, states={'confirmed': [('readonly', True)],
                                                                                                                                    'done': [('readonly', True)],
                                                                                                                                    'cancel': [('readonly', True)]},
        help="Warehouse where the vouchers will be moved to.")
    location_id = fields.Many2one(
        'stock.location', 'Shop / Location',
        readonly=False, required=True, index=True, domain=[('usage', '=', 'internal')],
        states={'confirmed': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]},
        help="Location where the vouchers will be moved to.")
    voucher_ids = fields.Many2many('voucher.voucher', string='Vouchers',
                                   readonly=False, states={'confirmed': [('readonly', True)],
                                                           'done': [('readonly', True)],
                                                           'cancel': [('readonly', True)]})
    move_date = fields.Datetime(
        'Date', copy=False, default=fields.Datetime.now, readonly=False,
        index=True, states={'confirmed': [('readonly', True)],
                            'done': [('readonly', True)],
                            'cancel': [('readonly', True)]})
    move_finished_ids = fields.One2many(
        'stock.move', 'move_order_id', 'Finished Move',
        copy=False, readonly=True)
    picking_id = fields.Many2one('stock.picking', string='Picking', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default='draft', tracking=True)

    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
        required=True)

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        if self.warehouse_id:
            self.location_id = self.warehouse_id.lot_stock_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('voucher.move.order') or '/'
        return super(VoucherMoveOrder, self).create(vals_list)

    def unlink(self):
        if any(order.state not in ('cancel', 'draft') for order in self):
            raise UserError(_('Could not delete a voucher move order not in draft or cancel state'))
        return super(VoucherMoveOrder, self).unlink()

    def action_confirm(self):
        for r in self:
            if not r.voucher_ids:
                raise UserError(_('You must select some vouchers for confirming this order.'))
            if any(voucher.state != 'new' for voucher in r.voucher_ids):
                raise UserError(_('All vouchers selected should be in inactivated state.'))
        self.write({'state': 'confirmed'})

    def action_draft(self):
        for r in self:
            r.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_move(self):
        for r in self:
            r._generate_moves(picking_id=False)
            picking_id = r._create_picking()
            r._update_move_dest(picking_id)
            r.write({'state': 'done', 'move_date': fields.Datetime.now(), 'picking_id': picking_id.id})

    def _prepare_stock_picking(self, picking_type_id):
        return {
            'location_id': picking_type_id.default_location_src_id.id,
            'location_dest_id': picking_type_id.default_location_dest_id.id,
            'scheduled_date': fields.Datetime.now(),
            'picking_type_id': picking_type_id.id
            }

    def _update_move_dest(self, picking_id):
        self.ensure_one()
        for move in self.move_finished_ids:
            move_dest = picking_id.move_lines.filtered(lambda x: x.product_id == move.product_id)
            if move_dest and not move.picking_id:
                move.write({'move_dest_ids': [(4, move_dest[0].id)]})

    def _create_picking(self):
        self.ensure_one()
        if not self.voucher_ids:
            raise UserError(_("No promotion voucher to move."))

        if len(self.voucher_ids.mapped('current_stock_location_id')) > 1:
            raise UserError(_("All the selected vouchers must have the same source location in order to move"))

        # Check if voucher receipt is available then create it if not
        if not self.warehouse_id.voucher_receipt_picking_type_id:
            self.warehouse_id._create_voucher_receipt_picking_type()

        picking_id = self.env['stock.picking'].create(self._prepare_stock_picking(self.warehouse_id.voucher_receipt_picking_type_id))
        self._generate_moves(picking_id)
        return picking_id

    def _prepare_stock_move_data(self, product, picking_id=False):
        voucher_ids = self.voucher_ids.filtered(lambda x: x.product_id.id == product.id)
        now = fields.Datetime.now()
        transit_location = self.env['stock.location'].search([
                ('usage', '=', 'transit'),
                ('company_id', '=', self.warehouse_id.company_id.id)
                ], limit=1)
        if not transit_location:
            raise UserError(_('Could not find transit location for the company: %s.') % self.company_id.name)
        return {
            'name': picking_id and self.name or _('Transit %s') % self.name,
            'date': now,
            'date_expected': now,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': len(voucher_ids),
            'location_id': picking_id and picking_id.location_id.id or self.voucher_ids[0].current_stock_location_id.id,
            'location_dest_id': picking_id and picking_id.location_dest_id.id or transit_location.id,
            'company_id': self.env.company.id,
            'origin': picking_id and self.name or _('Transit %s') % self.name,
            'move_order_id': self.id,
            'picking_type_id': picking_id and picking_id.picking_type_id.id or False,
            'picking_id': picking_id and picking_id.id or False
            }

    def _generate_moves(self, picking_id=False):
        for r in self.filtered(lambda o: o.voucher_ids):
            for product in r.voucher_ids.mapped('product_id'):
                voucher_ids = r.voucher_ids.filtered(lambda x: x.product_id.id == product.id)
                lot_ids = voucher_ids.mapped('lot_id')
                move = self.env['stock.move'].create(self._prepare_stock_move_data(product, picking_id))
                move._action_confirm()._action_assign()
                move.validate_promotion_voucher_move(lot_ids)
                if not picking_id:
                    move._action_done()
        return True
