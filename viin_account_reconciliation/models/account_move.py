# -*- coding: utf-8 -*-

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _recompute_invoice_amounts(self):
        """
        This recompute amount fields for the invoices (including receipts) in self
        """
        invoices = self.filtered(lambda inv: inv.is_invoice(include_receipts=True))
        if invoices:
            invoices._compute_amount()

