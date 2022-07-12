from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    price_tax = fields.Monetary(string='Tax Amount', compute='_get_price_tax', store=False)
    
    def _get_price_tax(self):
        for l in self:
            l.price_tax = l.price_total - l.price_subtotal