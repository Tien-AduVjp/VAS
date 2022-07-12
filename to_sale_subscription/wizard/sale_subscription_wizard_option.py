from odoo import models, fields, api


class SaleSubscriptionWizardOption(models.TransientModel):
    _name = 'sale.subscription.wizard.option'
    _description = 'Subscription Upsell Lines Wizard'

    name = fields.Char(string='Description')
    wizard_id = fields.Many2one('sale.subscription.wizard', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', required=True, domain="[('recurring_invoice', '=', True)]", ondelete='cascade')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True, ondelete='cascade', domain="[('category_id', '=', product_id.uom_id.category_id.id)]")
    quantity = fields.Float(default=1.0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        # TODO: convert this to compute method
        if self.product_id:
            self.name = self.product_id.get_product_multiline_description_sale()
            if not self.uom_id:
                self.uom_id = self.product_id.uom_id.id
