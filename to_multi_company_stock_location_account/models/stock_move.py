from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_src_account(self, accounts_data):
        if self.location_id.property_valuation_out_account_id:
            return self.location_id.property_valuation_out_account_id.id

        return super(StockMove, self)._get_src_account(accounts_data)

    def _get_dest_account(self, accounts_data):
        if self.location_id.property_valuation_in_account_id:
            return self.location_id.property_valuation_in_account_id.id

        return super(StockMove, self)._get_dest_account(accounts_data)
