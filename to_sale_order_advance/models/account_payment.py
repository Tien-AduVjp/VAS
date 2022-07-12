from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_order_ids = fields.Many2many('sale.order',
                                      string="Sales Orders",
                                      domain="[('state', 'not in', ['draft', 'sent']), ('partner_invoice_id', '=', partner_id)]")

    @api.onchange('sale_order_ids', 'currency_id', 'payment_date')
    def _onchange_sale_order_ids(self):
        sale_orders = self.sale_order_ids
        if sale_orders:
            self.partner_id = sale_orders[0].partner_invoice_id
            if not self.currency_id:
                self.currency_id = sale_orders[0].currency_id
            self.amount = self._calculate_advance_payment_amount_residual_with_so()

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountPayment, self)._onchange_partner_id()
        if self.partner_id not in self.sale_order_ids.partner_invoice_id:
            self.sale_order_ids = False
        return res

    @api.onchange('partner_type')
    def _onchange_partner_type_with_so(self):
        if self.sale_order_ids and self.partner_type != 'customer':
            self.sale_order_ids = False

    @api.constrains('sale_order_ids')
    def _check_constrains_partner_with_so(self):
        for r in self.filtered(lambda r: r.sale_order_ids):
            if r.partner_id != r.sale_order_ids.partner_invoice_id:
                raise ValidationError(_("The partner on payment '%s' and the sale order should be the same.") % r.name)

    def write(self, vals):
        old_vals = False
        if 'sale_order_ids' in vals:
            old_vals = self.read(['sale_order_ids'])

        res = super(AccountPayment, self).write(vals)

        if old_vals:
            new_vals = self.read(['sale_order_ids'])
            self._message_track_sale_order_ids(old_vals, new_vals)
        return res

    def _message_track_sale_order_ids(self, old_vals, new_vals):
        for r in self:
            old_val = {}
            for val in old_vals:
                if r.id == val.get('id', False):
                    old_val = val
                    break
            new_val = {}
            for val in new_vals:
                if r.id == val.get('id', False):
                    new_val = val
                    break
            old_sale_orders = self.env['sale.order'].browse(old_val.get('sale_order_ids', []))
            new_sale_orders = self.env['sale.order'].browse(new_val.get('sale_order_ids', []))
            if new_sale_orders:
                if not old_sale_orders:
                    body=_("""
                        <ul class="o_mail_thread_message_tracking">
                            <li>
                                Sales Orders:
                                <span>%s</span>
                            </li>
                        </ul>
                    """) % (', '.join(new_sale_orders.mapped('name')))
                else:
                    body=_("""
                        <ul class="o_mail_thread_message_tracking">
                            <li>
                                Sales Orders:
                                <span>%s</span>
                                <span class="fa fa-long-arrow-right" role="img" aria-label="Changed" title="Changed"/>
                                <span>%s</span>
                            </li>
                        </ul>
                    """) % (', '.join(old_sale_orders.mapped('name')), ', '.join(new_sale_orders.mapped('name')))
                r.message_post(body=body)

    def _calculate_advance_payment_amount_residual_with_so(self):
        self.ensure_one()
        amount_residual = 0
        for so in self.sale_order_ids:
            amount = so.amount_total - so.advance_payment_amount
            if so.currency_id != self.currency_id:
                amount = so.currency_id._convert(
                    amount,
                    self.currency_id,
                    so.company_id,
                    self.payment_date or so.date_order,
                    round=False
                    )
            amount_residual += amount
        return amount_residual

    def _calculate_advance_payment_amount_with_so(self, currency):
        advance_payment_amount = 0.0
        for r in self.filtered(lambda r: r.state not in ['draft', 'cancelled']):
            if r.currency_id != currency:
                payment_amount = r.currency_id._convert(
                    r.amount,
                    currency,
                    r.company_id,
                    r.payment_date,
                    round=True
                    )
            else:
                payment_amount = r.amount
            if r.payment_type == 'outbound':
                advance_payment_amount -= payment_amount
            else:
                advance_payment_amount += payment_amount
        return advance_payment_amount
