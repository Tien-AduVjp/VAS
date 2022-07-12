from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_landed_cost_ids = fields.One2many('product.landed.cost', 'product_template_id', string='Landed Costs',
                                              help="Predefined Landed Costs that can be added automatically during purchase of this product.")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_product_landed_costs(self):
        return self.env['product.landed.cost'].search([('auto_purchase', '=', True), ('product_template_id', 'in', self.mapped('product_tmpl_id').ids)])

