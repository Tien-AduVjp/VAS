from odoo import models


class AccountInvoiceEInvoiceCancel(models.TransientModel):
    _inherit = 'account.invoice.einvoice.cancel'

    def action_cancel_einvoice(self):
        res = super(AccountInvoiceEInvoiceCancel, self).action_cancel_einvoice()
        for r in self:
            if r.invoice_id.sinvoice_transactionid:
                r.invoice_id.with_context(
                    additionalReferenceDesc=r.additional_reference_desc,
                    additionalReferenceDate=r.additional_reference_date
                    )._cancel_sinvoice()
        return res
