from odoo import fields, models

class DocumentTag(models.Model):
    _name = 'document.tag'
    _description = "Document Tag"

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True, help="Can be used to show tooltip on some views")
    active = fields.Boolean(string='Active', default=True)
    category_ids = fields.Many2many('document.tag.category', string='Categories', required=True)
