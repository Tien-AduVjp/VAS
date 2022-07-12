from odoo import models,api


class PosSession(models.Model):
    _inherit = 'pos.session'
 
    
    def _get_sale_vals(self, key, amount, amount_converted):
        res = super(PosSession, self)._get_sale_vals(key, amount, amount_converted)
        res["analytic_account_id"] =  self.config_id.analytics_account_id.id        
        return res


    def _get_tax_vals(self, key, amount, amount_converted, base_amount_converted):
        res = super(PosSession, self)._get_tax_vals(key, amount, amount_converted, base_amount_converted)
        res["analytic_account_id"] =  self.config_id.analytics_account_id.id
        return res