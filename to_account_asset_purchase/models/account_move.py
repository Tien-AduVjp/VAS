from odoo import api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        res = super(AccountMove, self)._onchange_purchase_auto_complete()
        for line in self.invoice_line_ids:
            line._onchange_asset_category_id()
        return res
