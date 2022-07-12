from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    uom_3rd_id = fields.Many2one('uom.uom', related='product_tmpl_id.uom_3rd_id', readonly=True, store=True)