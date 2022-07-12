from odoo import fields, models


class TestType(models.Model):
    _name = "quality.point.test_type"
    _description = "Test Type"

    name = fields.Char(string='Name', required=True)
    technical_name = fields.Char(string='Technical name', required=True)
