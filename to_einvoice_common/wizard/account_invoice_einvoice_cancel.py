from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import format_date, format_datetime


class AccountInvoiceEInvoiceCancel(models.TransientModel):
    _name = 'account.invoice.einvoice.cancel'
    _description = 'E-Invoice Cancellation Wizard'

    invoice_id = fields.Many2one('account.move', string='Invoice to Cancel', required=True)
    additional_reference_desc = fields.Char(string='Reference', required=True,
                                            help="The name/reference of the agreement between you and your customer for the invoice cancellation.")
    additional_reference_date = fields.Datetime(string='Cancellation Date', required=True,
                                            help="The date and time of the agreement between you and your customer for the invoice cancellation.")
    cancellation_record = fields.Binary(related='invoice_id.cancellation_record', readonly=False)
    cancellation_record_name = fields.Char(related='invoice_id.cancellation_record_name', readonly=False)

    @api.constrains('additional_reference_date', 'invoice_id')
    def _check_additional_reference_date(self):
        for r in self:
            if r.additional_reference_date > fields.Datetime.now():
                raise ValidationError(_("The Cancellation Date must not be in the future"))
            if r.additional_reference_date < r.invoice_id.einvoice_invoice_date:
                raise ValidationError(_("The Cancellation Date must not be earlier than the issue date which is %s")
                                      % format_datetime(self.env, r.invoice_id.einvoice_invoice_date))

    def action_cancel_einvoice(self):
        for r in self:
            if r.cancellation_record_name:
                if r.cancellation_record_name[-4:] != '.pdf':
                    raise ValidationError(_("Only allow upload PDF file"))
