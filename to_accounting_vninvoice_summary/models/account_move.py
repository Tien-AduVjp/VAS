from odoo import models, _
from odoo.tools import float_round
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_vninvoice_data(self):
        if self.invoice_display_mode != 'invoice_line_summary_lines' or self.type == 'out_refund':
            return super(AccountMove, self)._prepare_vninvoice_data()
        
        self._portal_ensure_token()

        data = {
            'invoiceDate': self.invoice_date.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            'Note':'',
            'exchangeRate': float_round((1 / self.currency_id.with_context(date=self.invoice_date).rate), precision_digits=4),
            'paymentMethod':'Tiền mặt hoặc chuyển khoản',
            'paymentDate': self._get_payment_date().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            'totalAmount': float_round(self.amount_untaxed,precision_digits=2),
            'totalVatAmount': float_round(self.amount_tax, precision_digits=2),
            'totalPaymentAmount': float_round(self.amount_total, precision_digits=2),
            'totalDiscountAmountBeforeTax': 0.0,
            'totalDiscountPercentAfterTax': 0,
            'totalDiscountAmountAfterTax': 0.0,
            'buyerEmail': self.commercial_partner_id.email or '',
            'buyerFullName': self.commercial_partner_id.name,
            'buyerLegalName': self.partner_id.name if self.partner_id.company_type == 'person' else '',
            'buyerTaxCode': self.commercial_partner_id.vat or '',
            'buyerAddressLine': self._get_cusomter_invoice_address()._einvoice_display_address(),
            'buyerDistrictName':'',
            'buyerCityName': self.commercial_partner_id.city or self.commercial_partner_id.state_id.name or '',
            'buyerCountryCode': self.commercial_partner_id.country_id and self.commercial_partner_id.country_id.code or '',
            'buyerPhoneNumber': self.commercial_partner_id.phone and self._phone_format(self.commercial_partner_id.phone) or '',
            'buyerFaxNumber':'',
            'buyerBankName':'',
            'buyerBankAccount':'',
            # Mã đơn hàng / hợp đồng / mã tra cứu
            'userNameCreator': self._get_issuing_user().name,
            'idBuyer': str(self.commercial_partner_id.id) or '',
            'buyerGroupCode':'',
            'buyerCode': str(self.commercial_partner_id.id) or '',
            'idBuyerGroup':'',
            'buyerGroupName':'',
            'currency': self.currency_id.name,
            'invoiceDetails': self.invoice_line_summary_ids._prepare_einvoice_summary_lines_data(),
            'invoiceTaxBreakdowns': self._prepare_vninvoice_tax_breakdowns(),
        }
        if self.einvoice_api_version == 'v1':
            data.update({
                'templateNo': self._get_vninvoice_template_name(),
                'serialNo': self._get_account_vninvoice_serial_name(),
                'id': self.access_token,
                'idTransaction': self.access_token,
            })
        else:
            if not self._get_vninvoice_template_name().isdigit():
                raise UserError(_("You have to set E-invoice Template being only number, not include letter"))
            data.update({
                'templateNo': int(self._get_vninvoice_template_name()),
                'serialNo': self._get_account_vninvoice_serial_name(),
                'erpId': self.access_token,
                'creatorErp': self._get_issuing_user().name,
                'transactionId': self.access_token,
                'paymentMethod': 'TM/CK',
            })
        return [data]
