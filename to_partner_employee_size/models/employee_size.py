from odoo import fields, models


class PartnerEmployeeSize(models.Model):
    _name = 'res.partner.employee.size'
    _description = 'Partner Employee Size'
    
    name = fields.Char(string="Name", required=True, translate=True)
    description = fields.Text(string="Description", translate=True)