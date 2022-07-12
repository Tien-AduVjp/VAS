from odoo import models, fields

class QualityType(models.Model):
    _inherit = 'quality.type'

    type = fields.Selection(selection_add=[('product', 'Product')], ondelete={'product': 'set default'})
