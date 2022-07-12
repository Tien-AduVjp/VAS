from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    working_frequency_template_ids = fields.Many2many('working.frequency.template', string='Working Frequency')

    @api.constrains('working_frequency_template_ids')
    def _check_working_frequency_template_ids(self):
        for r in self:
            uom_categ_ids = r.working_frequency_template_ids.mapped('working_uom_id.category_id')
            if len(uom_categ_ids) < len(r.working_frequency_template_ids):
                raise ValidationError(_("Cannot set working frequency with the same Unit of Measure category in one product."))

