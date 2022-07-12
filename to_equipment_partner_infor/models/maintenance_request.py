# -*- coding: utf-8 -*-

from odoo import models, fields

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'
    
    customer_id = fields.Many2one('res.partner', string='Customer', readonly=True, related='equipment_id.customer_id', store=True)
