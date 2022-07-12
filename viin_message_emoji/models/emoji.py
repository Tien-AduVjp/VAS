from odoo import models, fields


class Emoji(models.Model):
    _name = 'emoji'
    _description = 'Message emoji'
    
    name = fields.Char(string='Name')
    emoji = fields.Char(string='Key')
