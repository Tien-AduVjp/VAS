from odoo import fields, models

class QualityReason(models.Model):
    _name = "quality.reason"
    _description = "Quality Reason"

    name = fields.Char(string='Name', translate=True, required=True)
