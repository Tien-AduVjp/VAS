import base64
from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools.mimetypes import guess_mimetype

class AccountInvoiceEInvoiceAdjustment(models.TransientModel):
    _name = 'account.invoice.einvoice.adjustment'
    _description = 'E-Invoice Adjustment Wizard'

    invoice_id = fields.Many2one('account.move', string='Invoice to Cancel', required=True)
    additional_reference_desc = fields.Char(string='Reference', required=True,
                                            help="The name/reference of the agreement between you and your customer for the invoice adjustment.")
    adjustment_record = fields.Binary(related='invoice_id.adjustment_record', readonly=False, required=True)
    adjustment_record_name = fields.Char(related='invoice_id.adjustment_record_name', readonly=False)

    def action_adjust_einvoice(self):
        for r in self:
            if not r.invoice_id.reversed_entry_id:
                raise UserError(
                    _("Cannot issue e-invoice because this invoice is not a reversal of any customer invoice"))
            if r.invoice_id.reversed_entry_einvoice_state not in ('issued', 'paid', 'adjusted'):
                raise UserError(
                    _("Cannot issue e-invoice because the original invoice %s is not in '%s' e-invoice state") %
                    (r.invoice_id.reversed_entry_id.display_name, r.invoice_id.reversed_entry_einvoice_state))
            content = base64.b64decode(r.adjustment_record)
            if guess_mimetype(content) != 'application/pdf':
                raise UserError(_("Only allow upload PDF file"))
            r.with_context(
                additionalReferenceDesc=r.additional_reference_desc,
            ).invoice_id.issue_einvoices()
