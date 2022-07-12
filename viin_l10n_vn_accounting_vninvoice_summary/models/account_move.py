from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_vninvoice_data(self):
        vninvoice_data = super(AccountMove, self)._prepare_vninvoice_data()
        if self.invoice_display_mode == 'invoice_line_summary_lines' and self.move_type != 'out_refund':
            vninvoice_data[0]['invoiceDetails'] = self.invoice_line_summary_ids._prepare_einvoice_summary_lines_data()
        return vninvoice_data
