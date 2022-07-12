from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    amount_paid_by_voucher = fields.Float(string='Amount Paid by Voucher', compute='_compute_amount_paid_by_voucher')
    voucher_ids = fields.One2many('voucher.voucher', 'pos_order_id', string='Vouchers')

    @api.depends('payment_ids', 'lines.price_subtotal_incl', 'lines.discount')
    def _compute_amount_paid_by_voucher(self):
        for r in self:
            r.amount_paid_by_voucher = sum(payment.amount for payment in r.payment_ids.filtered(lambda x: x.payment_method_id.voucher_payment))

    def _payment_fields(self, order, ui_paymentline):
        res = super(PosOrder, self)._payment_fields(order, ui_paymentline)
        voucher_id = ui_paymentline.get('voucher_id', False)
        if voucher_id == 0:
            voucher_id = False
        res['voucher_id'] = voucher_id
        return res

#     def _prepare_bank_statement_line_payment_values(self, data):
#         args = super(PosOrder, self)._prepare_bank_statement_line_payment_values(data)
#         args['voucher_id'] = data.get('voucher_id', False)
#         return args

    @api.model
    def _process_order(self, pos_order, draft, existing_order):
        """
        :param pos_order: data dict to create a PoS Order
        
        :return: pos.order record created with pos_order data
        """
        order_id = super(PosOrder, self)._process_order(pos_order, draft, existing_order)
        order = self.browse(order_id)
        for line in order.lines.filtered(lambda l: l.product_id.is_promotion_voucher):
            if line.pack_lot_ids:
                lot_name = line.pack_lot_ids.mapped('lot_name')
                lot_ids = self.env['stock.production.lot'].search([('name', 'in', lot_name)])
                voucher_ids = self.env['voucher.voucher'].search([('lot_id', 'in', lot_ids.ids)])
                voucher_ids.write({'pos_order_line_id': line.id})

        # process statement lines that link to voucher
        for st_line in order.payment_ids.filtered(lambda l: l.voucher_id):
            if st_line.payment_method_id.voucher_payment:
                st_line.voucher_id.write({
                    'used_amount': st_line.amount + st_line.voucher_id.used_amount,
                    'state': 'used',
                    'used_date': fields.Datetime.now()
                    })
        return order_id

    def _prepare_invoice(self):
        res = super(PosOrder, self)._prepare_invoice()
        res['amount_paid_by_voucher'] = self.amount_paid_by_voucher
        return res

    def _force_picking_done(self, picking):
        super(PosOrder, self)._force_picking_done(picking)
        if picking.state != 'done':
            voucher_moves = picking.move_lines.filtered(lambda x: x.product_id.is_promotion_voucher)
            voucher_moves._action_done()

