from odoo import fields, models


class PartnerBusinessType(models.Model):
    _name = 'res.partner.business.type'
    _description = 'Partner Business Type'
    
    name = fields.Char(string="Name", required=True, translate=True)
    description = fields.Text(string="Description", translate=True)
