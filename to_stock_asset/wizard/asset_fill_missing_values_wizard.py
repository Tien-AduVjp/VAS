from odoo import fields, models


class AssetFillMissingValuesWizard(models.TransientModel):
    _inherit = 'asset.fill.missing.values.wizard'

    production_lot_id = fields.Many2one('stock.production.lot', string='Lot/Seria Number')

    def _prepare_account_asset_vals(self):
        self.ensure_one()
        vals = super(AssetFillMissingValuesWizard, self)._prepare_account_asset_vals()
        if self.production_lot_id:
            vals.update({
                'production_lot_id': self.production_lot_id.id,
                })
        return vals
