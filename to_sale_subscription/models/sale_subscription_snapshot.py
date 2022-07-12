from odoo import fields, models


class SaleSubscriptionSnapshot(models.Model):
    _name = 'sale.subscription.snapshot'
    _description = 'Subscription Snapshot'

    subscription_id = fields.Many2one('sale.subscription', string='Subscription', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    recurring_monthly = fields.Float(string='Monthly Recurring Revenue', required=True)
