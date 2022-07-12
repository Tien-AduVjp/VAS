from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    collection_id = fields.Many2one('product.collection', string='Collection',
                                            index=True, ondelete='restrict')
