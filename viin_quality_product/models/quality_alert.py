from odoo import api, fields, models


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    product_tmpl_id = fields.Many2one('product.template', string='Product')
    product_id = fields.Many2one('product.product', string='Product Variant',
        domain="[('product_tmpl_id', '=', product_tmpl_id)]", compute='_compute_product_id', readonly=False, store=True)

    @api.depends('product_tmpl_id')
    def _compute_product_id(self):
        for r in self:
            if r.product_tmpl_id:
                variant_ids = r.product_tmpl_id.product_variant_ids.ids
                if variant_ids:
                    r.product_id = r.product_id if r.product_id.id in variant_ids else variant_ids[0]
            else:
                r.product_id = False
