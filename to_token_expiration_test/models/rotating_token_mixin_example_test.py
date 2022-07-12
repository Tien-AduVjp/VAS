from odoo import models, fields


class RotatingTokenMixinExampleTest(models.Model):
    _name = 'rotating.token.mixin.example.test'
    _inherit = 'rotating.token.mixin'
    _description = 'Model is created for testing'

    company_id = fields.Many2one('res.company', string='Company')
