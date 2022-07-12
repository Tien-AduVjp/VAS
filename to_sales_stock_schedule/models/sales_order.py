from datetime import timedelta
from odoo import models, fields, api


class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    date_expected = fields.Datetime(string='Est. Delivery', compute='_compute_date_expected', inverse='_set_date_expected',
                                    help='The date of delivery that you promise your customer.', store=True)

    @api.depends('customer_lead', 'order_id.date_order')
    def _compute_date_expected(self):
        for r in self:
            date_order = r.order_id.date_order or fields.Datetime.now()
            r.date_expected = date_order + timedelta(days=r.customer_lead or 0.0)

    def _set_date_expected(self):
        for r in self:
            if r.date_expected:
                date_order = r.order_id.date_order or fields.Datetime.now()
                r.customer_lead = (r.date_expected - date_order).total_seconds() / (60*60*24)
