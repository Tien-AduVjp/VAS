from odoo import models, fields, api

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    equipment_ids = fields.One2many('maintenance.equipment', 'lot_id', string='Equipments',
                                    help="The Equipments that refer to this lot")

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', compute='_compute_equipment_id', store=True, index=True,
                                   help="The Equipment that refers to this lot for equipment movement tracking.")
    maintenance_ids = fields.One2many('maintenance.request', 'lot_id', string='Maintenances')
    maintenance_history_count = fields.Integer(compute='_compute_maintenance_history', store=True)

    @api.depends('maintenance_ids')
    def _compute_maintenance_history(self):
        for r in self:
            r.maintenance_history_count = len(r.maintenance_ids)

    @api.depends('equipment_ids')
    def _compute_equipment_id(self):
        for r in self:
            if r.equipment_ids:
                r.equipment_id = r.equipment_ids[0]

    def action_view_maintenances_history(self):
        maintenance_ids = self.mapped('maintenance_ids')
        action = self.env.ref('maintenance.hr_equipment_request_action_from_equipment')
        res = action.read()[0]
        res['context'] = {}
        res['domain'] = "[('id', 'in', %s)]" % str(maintenance_ids.ids)
        return res