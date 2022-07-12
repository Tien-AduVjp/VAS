from odoo import models


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    def _prepare_move(self):
        self.ensure_one()
        res = super(AccountAssetDepreciationLine, self)._prepare_move()
        product = self.asset_id.production_lot_id.product_id
        if product:
            for line in res['line_ids']:
                line[2].update({'product_id': product.id})
        return res
