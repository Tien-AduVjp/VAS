from odoo import api, fields, models


class QualityAlertAction(models.Model):
    _inherit = 'quality.alert.action'

    product_id = fields.Many2one('product.product', related='quality_alert_id.product_id', store=True, readonly=True, index=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product',
                                      related='quality_alert_id.product_tmpl_id', store=True, readonly=True, index=True)
