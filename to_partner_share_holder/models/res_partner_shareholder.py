from odoo import fields,models

class Shareholder(models.Model):
    _name = 'res.partner.shareholder'
    _description = 'Partner Shareholder'
    
    partner_id = fields.Many2one('res.partner', string="Partner", required=True, ondelete='cascade')
    shareholder_id = fields.Many2one('res.partner', string="Shareholder", required=True, ondelete='cascade')
    owned_percentage = fields.Float(string="Owned Percentage")
    description = fields.Text(string="Description")
