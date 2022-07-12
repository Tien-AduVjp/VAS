from odoo import fields, models


class QualityAlertStage(models.Model):
    _name = "quality.alert.stage"
    _description = "Quality Alert Stage"
    _order = "sequence, id"
    _fold_name = 'folded'

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence')
    done = fields.Boolean(string='Alert Processed')
    folded = fields.Boolean(string='Folded')

