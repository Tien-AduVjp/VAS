from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    maintenance_schedule_ids = fields.Many2many('maintenance.schedule', string='Maintenance Schedule')

    maintenance_schedule_count = fields.Integer(string='Maintenance Schedule Count', compute='_compute_maintenance_schedule_count')

    @api.depends('maintenance_schedule_ids')
    def _compute_maintenance_schedule_count(self):
        for r in self:
            r.maintenance_schedule_count = len(r.maintenance_schedule_ids)
