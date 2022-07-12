from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'
    
    
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', related='production_lot_id.equipment_id', store=True)
    
    @api.constrains('state', 'equipment_id')
    def _constraint_state(self):
        equipment_ids = self.search([('id', 'not in', self.ids), ('state', '=', 'open')]).mapped('equipment_id').ids
        if equipment_ids:
            assets = self.filtered(lambda asset: asset.state == 'open' and asset.equipment_id.id in equipment_ids)
            if assets:
                raise UserError(_('Equipment \"%s\" for asset exists.') % assets[0].equipment_id.name)
