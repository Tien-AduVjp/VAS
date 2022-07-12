from odoo import models, fields

class Company(models.Model):
    _inherit = 'res.company'
     
    hotline= fields.Char(string='Hotline', related='partner_id.hotline', store=True, readonly=False)



    

    
    
