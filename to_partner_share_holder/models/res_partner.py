from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
        
    shareholder_ids = fields.One2many('res.partner.shareholder', 'partner_id', string="Shareholders")
    
    @api.onchange('company_type')
    def onchange_company_type(self):
        super(ResPartner, self).onchange_company_type()
        if self.company_type == 'person':
            self.shareholder_ids = False
