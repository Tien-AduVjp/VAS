from odoo import fields, models


class QualityAlertAction(models.Model):
    _inherit = 'quality.alert.action'

    lot_id = fields.Many2one('stock.production.lot', related='quality_alert_id.lot_id', store=True, readonly=True, index=True)
