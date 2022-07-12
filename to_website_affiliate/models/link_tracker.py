from odoo import models, fields

class link_tracker(models.Model):   
    _inherit = "link.tracker"    
    
    affiliate_code_id = fields.Many2one('affiliate.code', string='Affiliate Code')    
