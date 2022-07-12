from odoo import fields, models


class PartnerEquityRange(models.Model):
    _name = 'res.partner.equity.range'
    _description = 'Partner Equity Range'
    
    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
