from odoo import models, api


class StockInventory(models.Model):
    _inherit = 'stock.inventory'


    def action_validate(self):
        self.ensure_one()
        user = self.env.user
        access_users = self.location_ids.mapped('access_user_ids')
        if (not access_users or user in access_users) and self.user_has_groups('to_multi_warehouse_access_control.group_warehouse_manager'):
            self = self.with_context(multi_warehouse_group='to_multi_warehouse_access_control.group_warehouse_manager')
        return super(StockInventory, self).action_validate()
    
    @api.model
    def user_has_groups(self, groups):
        multi_warehouse_group = self._context.get('multi_warehouse_group', False)
        if multi_warehouse_group:
            groups += ',' + multi_warehouse_group
        return super(StockInventory, self).user_has_groups(groups)