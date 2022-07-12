from odoo import models, fields, api


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    parent_equipment_ids = fields.Many2many('maintenance.equipment', 'maintenance_parent_equipment', 'maintenance_id', 'equipment_id',
                                            string='Also for', compute='_compute_parent_equipments', store=True,
                                            help="A maintenance of an equipment part is considered as a maintenance for all the other equipments"
                                            " that contain the equipment of the maintenance")

    child_maintenance_ids = fields.Many2many('maintenance.request', 'maintenance_child_maintenance', 'maintenance_id', 'child_maintenance_id',
                                           string='Sub-maintenance',
                                           compute='_compute_child_maintenances', store=True,
                                           help="The maintenances of the parts of the equipment of this maintenance")

    @api.depends('equipment_id.recursive_parent_ids')
    def _compute_parent_equipments(self):
        for r in self:
            r.parent_equipment_ids = r.equipment_id.recursive_parent_ids

    @api.depends('equipment_id.child_maintenance_ids', 'equipment_id.child_maintenance_ids.stage_id.done')
    def _compute_child_maintenances(self):
        for r in self:
            r.child_maintenance_ids = r.equipment_id.child_maintenance_ids.filtered(lambda x: not x.stage_id.done)
