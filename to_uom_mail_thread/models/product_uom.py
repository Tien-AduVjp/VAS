from odoo import models, fields

class ProductUoM(models.Model):
    _name = 'uom.uom'   
    _inherit = ['uom.uom', 'mail.thread']
    
    name = fields.Char(tracking=True)
    category_id = fields.Many2one(tracking=True)
    factor = fields.Float(tracking=True)
    factor_inv = fields.Float(tracking=True)
    rounding = fields.Float(tracking=True)
    uom_type = fields.Selection(tracking=True)
    
    