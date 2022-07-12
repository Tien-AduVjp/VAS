from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'


    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        #Remove assignment information on equipment when stock-in asset
        assets = self.sudo().mapped('stock_move_id.move_line_ids') \
                    .filtered(lambda line: line.location_dest_id.usage == 'internal' and line.account_asset_asset_id) \
                    .mapped('account_asset_asset_id')
        for asset in assets:
            equipment = asset.sudo().equipment_id
            if equipment:
                equipment.write(equipment._prepare_equipment_assignment_vals())
        return res
