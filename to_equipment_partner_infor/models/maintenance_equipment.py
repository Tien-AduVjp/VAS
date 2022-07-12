from odoo import models, fields


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    
    warranty_date = fields.Date(related='lot_id.warranty_expiration_date')
    partner_id = fields.Many2one(related='lot_id.supplier_id')
    customer_id = fields.Many2one('res.partner', string='Customer', domain="[('customer', '=', True)]", related='lot_id.customer_id')
