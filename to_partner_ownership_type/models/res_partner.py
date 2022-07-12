from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit='res.partner'
        
    ownership_type_id = fields.Many2one('res.partner.ownership.type', string="Ownership Type", tracking=True,  ondelete='restrict')
    
    @api.onchange('company_type')
    def onchange_company_type(self):
        super(ResPartner, self).onchange_company_type()
        if self.company_type == 'person':
            self.ownership_type_id = False