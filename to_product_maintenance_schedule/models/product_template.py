from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    maintenance_schedule_ids = fields.Many2many('maintenance.schedule', string='Maintenance Schedule')
    maintenance_schedule_count = fields.Integer(string='Maintenance Schedule Count', compute='_compute_maintenance_schedule_count')

    def _compute_maintenance_schedule_count(self):
        for r in self:
            r.maintenance_schedule_count = len(r.maintenance_schedule_ids)
