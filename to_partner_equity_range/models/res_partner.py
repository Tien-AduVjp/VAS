from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
        
    equity_range_id = fields.Many2one('res.partner.equity.range', string="Equity Range", ondelete='restrict', tracking=True)
    
    @api.onchange('company_type')
    def onchange_company_type(self):
        super(ResPartner, self).onchange_company_type()
        if self.company_type == 'person':
            self.equity_range_id = False