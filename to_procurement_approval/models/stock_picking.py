from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    approval_request_id = fields.Many2one('approval.request', string= 'Approval request')