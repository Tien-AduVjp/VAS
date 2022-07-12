from odoo import fields, models


class AccountAssetAssetAddWizard(models.TransientModel):
    _inherit = 'account.asset.asset.add.wizard'
    
    
    production_lot_id = fields.Many2one('stock.production.lot', string='Lot/Seria Number')
    
    def _prepare_account_asset_vals(self):
        self.ensure_one()
        vals = super(AccountAssetAssetAddWizard, self)._prepare_account_asset_vals()
        if self.production_lot_id:
            vals.update({
                'production_lot_id': self.production_lot_id.id,
                })
        return vals
