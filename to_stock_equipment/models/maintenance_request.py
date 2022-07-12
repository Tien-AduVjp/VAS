from odoo import models, fields


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.request'

    lot_id = fields.Many2one('stock.production.lot', string="Lot/Serial", related='equipment_id.lot_id', store=True)
