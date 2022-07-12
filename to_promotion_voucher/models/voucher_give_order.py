from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VoucherGiveOrder(models.Model):
    _name = 'voucher.give.order'
    _description = 'Give Vouchers'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'give_date asc,id'

    name = fields.Char(
        'Reference', copy=False, readonly=True, default='/')
    origin = fields.Char(
        'Source', copy=False,
        help="Reference of the document that generated this order request.")

    partner_id = fields.Many2one('res.partner', string='Customer')

    voucher_ids = fields.Many2many('voucher.voucher', string='Vouchers',
                                   copy=False,
                                   readonly=False, states={'confirmed': [('readonly', True)],
                                                           'done': [('readonly', True)],
                                                           'cancel': [('readonly', True)]})
    give_date = fields.Datetime(
        'Date', copy=False, default=fields.Datetime.now, readonly=False,
        index=True, states={'confirmed': [('readonly', True)],
                            'done': [('readonly', True)],
                            'cancel': [('readonly', True)]})
    move_finished_ids = fields.One2many(
        'stock.move', 'give_order_id', 'Finished Move',
        copy=False, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default='draft', tracking=True)

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
        required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('voucher.give.order') or '/'
        return super(VoucherGiveOrder, self).create(vals_list)

    def unlink(self):
        if any(order.state not in ('cancel', 'draft') for order in self):
            raise UserError(_('Could not delete an order that is neither in draft nor cancel state'))
        return super(VoucherGiveOrder, self).unlink()

    def action_confirm(self):
        for r in self:
            if not r.voucher_ids:
                raise UserError(_('You must select some vouchers for confirming this order.'))
            if any(voucher.state != 'new' for voucher in r.voucher_ids):
                raise UserError(_('All vouchers selected should be in inactivated state.'))
        self.write({'state': 'confirmed'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_give(self):
        self._generate_stock_moves()
        self.write({
            'state': 'done',
            'give_date': fields.Datetime.now()
            })

    def _prepare_stock_move_data(self, product):
        voucher_ids = self.voucher_ids.filtered(lambda x: x.product_id.id == product.id)
        location_des_id = self.env.ref('stock.stock_location_customers')
        if not location_des_id:
            raise UserError(_('Can not found Customer Location.'))
        now = fields.Datetime.now()
        return {
            'name': self.name,
            'date': now,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': len(voucher_ids),
            'location_id': voucher_ids[0].current_stock_location_id.id,
            'location_dest_id': location_des_id.id,
            'company_id': self.company_id.id,
            'origin': self.name,
            'give_order_id': self.id,
            }

    def _generate_stock_moves(self):
        """
        Generate stock moves for vouchers from their current location to customer location

        :return: generated stock mmove recordset
        """
        moves = self.env['stock.move']
        for r in self.filtered(lambda o: o.voucher_ids):
            if len(r.voucher_ids.current_stock_location_id) > 1:
                raise UserError(_("All the selected vouchers must have the same source location to give"))
            product_ids = r.voucher_ids.product_id
            for product in product_ids:
                voucher_ids = r.voucher_ids.filtered(lambda x: x.product_id.id == product.id)
                lot_ids = voucher_ids.lot_id
                move = self.env['stock.move'].create(r._prepare_stock_move_data(product))
                move._action_confirm()._action_assign()
                move.validate_promotion_voucher_move(lot_ids)
                move._action_done()
                moves |= move
        return moves
