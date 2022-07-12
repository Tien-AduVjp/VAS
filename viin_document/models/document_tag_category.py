from odoo import fields, models

class DocumentTagCategory(models.Model):
    _name = 'document.tag.category'
    _description = "Document Tag Category"

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description')
    tag_ids = fields.Many2many('document.tag', string='Tags')
    active = fields.Boolean(string='Active', default=True)
