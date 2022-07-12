from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'product.product')], string='Attachments')
