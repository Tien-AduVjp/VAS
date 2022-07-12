from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    purchase_order_ids = fields.Many2many('purchase.order', string="Purchases Orders",
                                          domain="[('state', 'not in', ['draft', 'sent']), ('partner_id', '=', partner_id)]")

    @api.onchange('purchase_order_ids', 'currency_id', 'date')
    def _onchange_purchase_order_ids(self):
        purchase_orders = self.purchase_order_ids
        if purchase_orders:
            self.partner_id = purchase_orders[0].partner_id
            if not self.currency_id:
                self.currency_id = purchase_orders[0].currency_id
            self.amount = self._calculate_advance_payment_amount_residual_with_po()

    @api.onchange('partner_id')
    def _onchange_partner_id_po(self):
        if self.purchase_order_ids and self.partner_id not in self.purchase_order_ids.partner_id:
            self.purchase_order_ids = False
            self.amount = 0

    @api.onchange('partner_type')
    def _onchange_partner_type_with_po(self):
        if self.purchase_order_ids and self.partner_type != 'supplier':
            self.purchase_order_ids = False
            self.amount = 0

    @api.constrains('purchase_order_ids')
    def _check_constrains_partner_with_po(self):
        for r in self.filtered(lambda r: r.purchase_order_ids):
            if r.partner_id != r.purchase_order_ids.partner_id:
                raise ValidationError(_("The partner on payment '%s' and the purchase order should be the same.") % r.name)

    def write(self, vals):
        old_vals = False
        if 'purchase_order_ids' in vals:
            old_vals = self.read(['purchase_order_ids'])

        res = super(AccountPayment, self).write(vals)

        if old_vals:
            new_vals = self.read(['purchase_order_ids'])
            self._message_track_purchase_order_ids(old_vals, new_vals)
        return res

    def _message_track_purchase_order_ids(self, old_vals, new_vals):
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
            old_purchase_orders = self.env['purchase.order'].browse(old_val.get('purchase_order_ids', []))
            new_purchase_orders = self.env['purchase.order'].browse(new_val.get('purchase_order_ids', []))
            if old_purchase_orders != new_purchase_orders:
                if not old_purchase_orders:
                    body=_("""
                        <ul class="o_mail_thread_message_tracking">
                            <li>
                                Purchases Orders:
                                <span>%s</span>
                            </li>
                        </ul>
                    """) % (', '.join(new_purchase_orders.mapped('name')))
                else:
                    body=_("""
                        <ul class="o_mail_thread_message_tracking">
                            <li>
                                Purchases Orders:
                                <span>%s</span>
                                <span class="fa fa-long-arrow-right" role="img" aria-label="Changed" title="Changed"/>
                                <span>%s</span>
                            </li>
                        </ul>
                    """) % (', '.join(old_purchase_orders.mapped('name')), ', '.join(new_purchase_orders.mapped('name')))
                r.message_post(body=body)

    def _calculate_advance_payment_amount_residual_with_po(self):
        self.ensure_one()
        amount_residual = 0
        for po in self.purchase_order_ids:
            amount = po.amount_total - po.advance_payment_amount
            if po.currency_id != self.currency_id:
                amount = po.currency_id._convert(amount,
                                                 self.currency_id,
                                                 po.company_id,
                                                 self.date or po.date_order,
                                                 round=False)
            amount_residual += amount
        return amount_residual
