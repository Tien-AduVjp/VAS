from odoo import models, fields


class MaintenanceEquipment(models.Model):
    _name = 'maintenance.equipment'
    _inherit = ['maintenance.equipment', 'image.mixin']

    worksheet = fields.Binary(string='Worksheet', help="The PDF document concerning to this equipment (e.g. Instructions, Manual, Worksheet)")
