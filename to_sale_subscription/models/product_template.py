from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    recurring_invoice = fields.Boolean(string='Subscription Product', help="If enabled, confirming a sale order with this product will"
                                       " generate a subscription for recurring invoices")
    subscription_template_id = fields.Many2one('sale.subscription.template', string='Subscription Template',
        help="Product template for subscription")

