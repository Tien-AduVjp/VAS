from odoo import fields, models


class SaleSubscriptionCloseReason(models.Model):
    _name = 'sale.subscription.close.reason'
    _order = 'sequence, id'
    _description = 'Sale Subscription Close Reason'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(string='Active', default=True)
