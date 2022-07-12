from odoo import fields, models


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    repair_ids = fields.One2many('repair.order', 'lot_id', string="Repairs",
                                 groups='to_repair_access_group.group_repair_manager,stock.group_stock_user')
    repair_count = fields.Integer(string='Repair Count', compute="_compute_repair_count", compute_sudo=True,
                                  groups='to_repair_access_group.group_repair_manager,stock.group_stock_user')

    def _compute_repair_count(self):
        repair_orders_data = self.env['repair.order'].read_group([('lot_id', 'in', self.ids)], ['lot_id'], ['lot_id'])
        mapped_data = dict([(dict_data['lot_id'][0], dict_data['lot_id_count']) for dict_data in repair_orders_data])
        for r in self:
            r.repair_count = mapped_data.get(r.id, 0)

    def action_view_repair_history(self):
        self.ensure_one()
        action = self.env.ref('to_repair_extend.action_repair_history').read()[0]
        action['context'] = {'search_default_lot_id': self.id}
        return action

