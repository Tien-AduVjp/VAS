from odoo import fields, models

class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    is_custom_clearance = fields.Boolean(string="Is Custom Clearance Location?",
                                         help='Check this to indicate the location is a custom clearance location')    

    custom_authority_id = fields.Many2one('res.partner', string='Custom Authority',
                                          help='The custom authority at this custom clearance location')