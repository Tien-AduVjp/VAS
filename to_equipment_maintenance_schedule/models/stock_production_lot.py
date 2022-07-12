from odoo import fields, models, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    maintenance_schedule_ids = fields.Many2many(
        'maintenance.schedule', 
        string='Maintenance Schedule', 
        readonly=False, 
        compute='_compute_maintenance_schedule_ids', 
        inverse='_inverse_maintenance_schedule_ids')
    maintenance_schedule_count = fields.Integer(string='Maintenance Schedule Count', compute='_compute_maintenance_schedule_count')

    @api.depends('maintenance_schedule_ids')
    def _compute_maintenance_schedule_count(self):
        for r in self:
            r.maintenance_schedule_count = len(r.maintenance_schedule_ids)
    
    @api.depends('equipment_id.maintenance_schedule_ids')
    def _compute_maintenance_schedule_ids(self):
        for r in self:
            r.maintenance_schedule_ids = [(6, 0, r.equipment_id.maintenance_schedule_ids.ids)]
              
    def _inverse_maintenance_schedule_ids(self):
        for r in self:
            r.equipment_id.maintenance_schedule_ids = [(6, 0, r.maintenance_schedule_ids.ids)]
