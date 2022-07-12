from odoo import api, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('categ_id', 'tracking')
    def _check_categ_specific_identification(self):
        for r in self:
            if r.categ_id.property_cost_method == 'specific_identification' and r.tracking == 'none':
                raise UserError(_("Costing method of category 'Specific Identification' only available "
                                "for product tracking by a lot/serial number. Please change costing method of category or set tracking for product."))
