from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    uom_3rd_id = fields.Many2one(
        'uom.uom', '3rd Unit of Measure',
        help="The optinal third Unit of Measure for a product used for others to extend in some cases. It must be in the same category than the default unit of measure.")
    
    @api.constrains('uom_id', 'uom_3rd_id')
    def _check_uom(self):
        if any(template.uom_id and template.uom_3rd_id and template.uom_id.category_id != template.uom_3rd_id.category_id for template in self):
            raise ValidationError(_('Error: The default Unit of Measure and the 3rd Unit of Measure must be in the same category.'))
        return True
    
    @api.onchange('uom_id')
    def _onchange_uom_id(self):
        super(ProductTemplate, self)._onchange_uom_id()
        if self.uom_id:
            self.uom_3rd_id = self.uom_id.id