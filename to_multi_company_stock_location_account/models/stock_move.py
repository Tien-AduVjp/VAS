from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_accounting_data_for_valuation(self):
        """ Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant. """
        journal_id, acc_src, acc_dest, acc_valuation = super(StockMove, self)._get_accounting_data_for_valuation()

        if self.location_id.property_valuation_out_account_id:
            acc_src = self.location_id.property_valuation_out_account_id.id

        if self.location_dest_id.property_valuation_in_account_id:
            acc_dest = self.location_dest_id.property_valuation_in_account_id.id

        return journal_id, acc_src, acc_dest, acc_valuation
