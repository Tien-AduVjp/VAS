from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', related='production_lot_id.equipment_id', store=True)

    @api.constrains('state', 'equipment_id')
    def _check_same_equipment_id(self):
        equipment_ids = self.search([('id', 'not in', self.ids), ('state', '=', 'open')]).mapped('equipment_id').ids
        if equipment_ids:
            assets = self.filtered(lambda asset: asset.state == 'open' and asset.equipment_id.id in equipment_ids)
            if assets:
                raise UserError(_('Equipment \"%s\" for asset exists.') % assets[0].equipment_id.name)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountAssetAsset, self).create(vals_list)
        res._update_asset_status_on_equipment()
        return res

    def write(self, vals):
        res = super(AccountAssetAsset, self).write(vals)
        if 'state' in vals:
            self._update_asset_status_on_equipment()
        return res

    def _update_asset_status_on_equipment(self):
        for r in self.sudo().filtered(lambda r: r.equipment_id):
            r.equipment_id.write({
                'asset_status': r.state,
                })
        return True
