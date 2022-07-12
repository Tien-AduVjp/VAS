from odoo import fields, models


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    days_to_notify = fields.Integer(string='Days to Notify', default=7, tracking=True)
