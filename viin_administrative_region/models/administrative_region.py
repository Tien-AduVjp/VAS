from odoo import fields, models


class AdministrativeRegion(models.Model):
    _name = 'administrative.region'
    _description = 'Administrative Region'
    _inherit = 'mail.thread'
    
    name = fields.Char(string='Name', required=True, translate=True, tracking=True)
    country_id = fields.Many2one('res.country', string='Country', required=True, tracking=True)
    currency_id = fields.Many2one(related="country_id.currency_id", store=True)
    
    def name_get(self):
        return self.mapped(lambda r: (r.id, "[%s] %s" %(r.name, r.country_id.name)))
