from odoo import fields, models


class QualityPoint(models.Model):
    _inherit = "quality.point"

    code = fields.Selection(related='picking_type_id.code', string='Picking Type Code')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Workcenter')

