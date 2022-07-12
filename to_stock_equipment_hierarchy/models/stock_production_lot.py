from odoo import models, fields, api


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'


    recursive_maintenance_ids = fields.Many2many('maintenance.request', 'production_lot_maintenance_recursive', 'production_lot_id', 'maintenance_id',
                                                 string='Recursive Maintenances',
                                                 compute='_compute_recursive_maintenance_ids', store=True,
                                                 help="All the maintenances of this equipment and its parts")

    recursive_maintenances_count = fields.Integer(string='Maintenances Count', compute='_compute_recursive_maintenances_count', store=True)

    @api.depends('recursive_maintenance_ids')
    def _compute_recursive_maintenances_count(self):
        for r in self:
            r.recursive_maintenances_count = len(r.recursive_maintenance_ids)

    @api.depends('equipment_id.recursive_maintenance_ids')
    def _compute_recursive_maintenance_ids(self):
        for r in self:
            r.recursive_maintenance_ids = r.equipment_id.recursive_maintenance_ids

    def action_view_recursive_maintenances(self):
        recursive_maintenance_ids = self.mapped('recursive_maintenance_ids')
        action = self.env['ir.actions.act_window']._for_xml_id('maintenance.hr_equipment_request_action_from_equipment')
        action['domain'] = "[('id', 'in', %s)]" % (recursive_maintenance_ids.ids)
        return action
