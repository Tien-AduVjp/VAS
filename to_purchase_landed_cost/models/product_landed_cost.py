from odoo import models, fields, api


class ProductLandedCost(models.Model):
    _name = 'product.landed.cost'
    _description = 'Product Landed Cost'
    _rec_name = 'product_id'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)

    product_template_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade', index=True,
                                          help="The product on which this landed cost would be applied during purchase")
    product_id = fields.Many2one('product.product', string='Landed Cost Product', required=True, ondelete='cascade', index=True,
                                 help="A product that presents a landed cost that may affect to this Product Template."
                                 " For example, transportation fee, stowage fee, etc")

    description = fields.Text(string='Description', translate=True)
    auto_purchase = fields.Boolean(string='Auto-Purchase', default=True,
                                 help="Check this to get another draft Purchase Order generated for this landed cost item when validating a Purchase Order")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.product_id.description_purchase:
            self.description = self.product_id.description_purchase

