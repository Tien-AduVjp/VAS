from odoo import fields, models


class QualityAlert(models.Model):
    _inherit = "quality.alert"

    production_id = fields.Many2one('mrp.production', "Production Order")
    work_order_id = fields.Many2one('mrp.workorder', 'Work Order')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center')
