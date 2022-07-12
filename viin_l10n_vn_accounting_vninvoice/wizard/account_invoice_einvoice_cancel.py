from odoo import models, fields

class AccountInvoiceEInvoiceCancel(models.TransientModel):
    _inherit = 'account.invoice.einvoice.cancel'

    reason = fields.Text(string='Reason', help="the reason of the agreement between you and your customer for the invoice cancellation.")

    def action_cancel_einvoice(self):
        res = super(AccountInvoiceEInvoiceCancel, self).action_cancel_einvoice()
        for r in self:
            if r.einvoice_provider == 'vninvoice':
                r.invoice_id.with_context(
                    fileNameOfRecord=r.cancellation_record_name,
                    recordDate=r.additional_reference_date,
                    recordNo=r.additional_reference_desc,
                    reason = r.reason,
                    fileOfRecord=r.cancellation_record.decode('UTF-8')
                    )._cancel_vninvoice()
        return res
