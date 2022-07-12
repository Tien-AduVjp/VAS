from odoo import models, fields, api

class QualityType(models.Model):
    _name = 'quality.type'
    _description = 'Quality Type'

    name = fields.Char(string='Name', required=True, translate=True)
    type = fields.Selection([('general', 'General')], string='Type', default='general', required=True)
