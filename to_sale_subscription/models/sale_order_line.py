from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _


PERIODS = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    subscription_id = fields.Many2one('sale.subscription', string='Subscription', copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            order_id = vals.get('order_id', False)
            product_id = vals.get('product_id', False)
            if order_id and product_id:
                order = self.env['sale.order'].browse(order_id)
                if order.origin and order.subscription_state in ('upsell', 'renew') and self.env['product.product'].browse(product_id).recurring_invoice:
                    subscription = self.env['sale.subscription'].search([('code', '=', order.origin)], limit=1)
                    if subscription:
                        vals['subscription_id'] = subscription.id
        return super(SaleOrderLine, self).create(vals_list)

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        if self.subscription_id:
            res.update({
                'subscription_id': self.subscription_id.id,
                })
            if self.subscription_id.analytic_account_id:
                res.update({
                'account_analytic_id': self.subscription_id.analytic_account_id.id,
                })
            if self.order_id.subscription_state != 'upsell':
                next_date = self.subscription_id.recurring_next_date
                previous_date = next_date - relativedelta(**{PERIODS[self.subscription_id.recurring_rule_type]: self.subscription_id.recurring_interval})
                lang = self.order_id.partner_invoice_id.lang
                format_date = self.env['ir.qweb.field.date'].with_context(lang=lang).value_to_html

                # workaround to display the description in the correct language
                if lang:
                    self = self.with_context(lang=lang)
                period_msg = _("Invoicing period: %s - %s") % (format_date(previous_date, {}), format_date(next_date - relativedelta(days=1), {}))
                res.update({
                    'name': (res['name'] + '\n' + period_msg),
                })
        return res

    def _prepare_subscription_line_vals(self):
        self.ensure_one()
        return {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': self.product_uom_qty,
            'uom_id': self.product_uom.id,
            'price_unit': self.price_unit,
            'discount':  self.order_id.subscription_state != 'upsell' and self.discount or False,
            }
    
    def _prepare_subscription_line_vals_list(self):
        return [r._prepare_subscription_line_vals() for r in self]

    def _prepare_subscription_line_data(self):
        return [(0, False, vals) for vals in self._prepare_subscription_line_vals_list()]

    def _prepare_update_subscription_line_vals_list(self, subscription):
        vals_list = []
        vals = {}
        for r in self:
            sub_lines = subscription.line_ids.filtered(lambda l: l.product_id.id == r.product_id.id and l.uom_id.id == r.product_uom.id)
            count = len(sub_lines)
            if count == 1:
                vals.setdefault(sub_lines.id, sub_lines.quantity)
                vals[sub_lines.id] += r.product_uom_qty
            elif count > 1:
                sub_lines[0].copy({'name': r.display_name, 'quantity': r.product_uom_qty})
            else:
                vals_list.append(r._prepare_subscription_line_data()[0])

        vals_list += [(1, sub_id, {'quantity': vals[sub_id], }) for sub_id in vals]
        return vals_list
