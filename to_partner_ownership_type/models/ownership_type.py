from odoo import fields, models


class PartnerBusinessType(models.Model):
    _name = 'res.partner.ownership.type'
    _description = 'Partner Business Type'
    
    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
