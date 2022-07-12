from odoo import fields, models

class QualityTag(models.Model):
    _name = "quality.tag"
    _description = "Quality Tag"

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index', default=0)
