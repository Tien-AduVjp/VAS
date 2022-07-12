import base64
import logging
import requests, json
import time

from odoo import models, api, fields, registry, _
from odoo.exceptions import UserError, ValidationError, MissingError
from odoo.tools import format_date
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)

# Viettel S-Invoice' representation file types
SINVOICE_REPRESENTATION_FILETYPE = ['PDF', 'ZIP']
# Viettel implements asynch mechanism
SINVOICE_TIMEOUT = 20000


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'to.vietnamese.number2words']

    sinvoice_reservation_code = fields.Char('S-Invoice Secret Code', copy=False, readonly=True)
    sinvoice_representation_pdf = fields.Binary(string='S-Invoice Representation File (PDF)', attachment=True, readonly=True, copy=False,
                                                 help="The display version of the S-Invoice in PDF format")
    sinvoice_representation_filename_pdf = fields.Char(string='S-Invoice Representation Filename (PDF)', readonly=True, copy=False)
    sinvoice_representation_zip = fields.Binary(string='S-Invoice Representation File (Zip)', attachment=True, readonly=True, copy=False,
                                                 help="The display version of the S-Invoice in Zip format. The zip archive shall"
                                                 " contain an xml version of the invoice.")
    sinvoice_representation_filename_zip = fields.Char(string='S-Invoice Representation Filename (Zip)', readonly=True, copy=False)
    sinvoice_converted_file = fields.Binary(string='S-Invoice Converted File', attachment=True, readonly=True, copy=False)
    sinvoice_converted_filename = fields.Char(string='S-Invoice Converted Filename', readonly=True, copy=False)
    # TODO: fields above will be moved to einvoice_common in odoo14
    sinvoice_representation_file_created = fields.Boolean("Electric Representation Invoice Downloaded?", copy=False, readonly=True, default=False)
    sinvoice_exchange_file_created = fields.Boolean("Electric Exchange Invoice Downloaded?", copy=False, readonly=True, default=False)
    sinvoice_transactionid = fields.Char(string='S-Invoice Transaction ID', copy=False, readonly=True,
                                         help="Technical field to store transaction ID that was returned by S-Invoice after invoice creation.")
    account_sinvoice_serial_id = fields.Many2one('account.sinvoice.serial', string='S-Invoice Serial', copy=False, readonly=True, ondelete='restrict')
    account_sinvoice_template_id = fields.Many2one('account.sinvoice.template', string='S-Invoice Template', copy=False, readonly=True, ondelete='restrict')
    account_sinvoice_type_id = fields.Many2one('account.sinvoice.type', string='S-Invoice Type', copy=False, readonly=True, ondelete='restrict')

    def _get_sinvoice_date(self):
        return fields.Datetime.to_datetime(self.invoice_date)

    def _get_account_sinvoice_serial_name(self):
        """
        Return the name of the sinvoice serial. For example, 'AA/18E', 'AA/19E'
        :rtype: string
        """
        if self.account_sinvoice_serial_id:
            return self.account_sinvoice_serial_id.name
        else:
            return self.journal_id.get_account_sinvoice_serial().name

    def _get_sinvoice_template_name(self):
        """
        Return the name of the sinvoice template. For example, '01GTKT0/001', '01GTKT0/002'
        :rtype: string
        """
        if self.account_sinvoice_template_id:
            return self.account_sinvoice_template_id.name
        else:
            return self.journal_id.get_sinvoice_template().name

    def _get_account_sinvoice_type_name(self):
        """
        Return the code of the sinvoice type. For example, '01GTKT', '02GTTT'
        :rtype: string
        """
        if self.account_sinvoice_type_id:
            return self.account_sinvoice_type_id.name
        else:
            return self.journal_id.get_account_sinvoice_type().name
        
    def _prepare_sinvoice_seller_bank(self):
        bank_info = {'bank_account':'', 'bank_name':''}
        for bank_journal_id in self.env.company.bank_journal_ids.filtered(lambda bank_journal_id: bank_journal_id.einvoice_display_bank_account == True and bank_journal_id.bank_id) :
            if bank_journal_id.bank_id.bic :
                bank_info['bank_name'] += bank_journal_id.bank_id.name + ', Swift/bic: ' + bank_journal_id.bank_id.bic+ ';'
            else:
                bank_info['bank_name'] += bank_journal_id.bank_id.name + ';'
            bank_info['bank_account'] += bank_journal_id.bank_account_id.acc_number + ';'
        bank_info['bank_name'] = bank_info['bank_name'][:-1]
        bank_info['bank_account'] = bank_info['bank_account'][:-1]
        if self.env.company.sinvoice_max_len_bank_account < len(bank_info['bank_account']) or self.env.company.sinvoice_max_len_bank_name < len(bank_info['bank_name']):
            raise ValidationError(_("Max length bank name or bank account are greater than allowed values (settings/accounting/sinvoice)"))
        return bank_info
    
    def _prepare_sinvoice_strIssueDate(self):
        """
        S-Invoice requires invoice date in the format of '%Y%m%d%H%M%S' (e.g. 20191202201243)
        """
        return self.invoice_date.strftime('%Y%m%d%H%M%S')

    def _get_sinvoice_presentation_data(self, file_type):
        """
        This method will connect S-Invoice and request for representated data that could be used for displaying purpose
        
        @param file_type: the file type to get which is either 'ZIP' or 'PDF'
        :return: dictionary of return data
            {
                'errorCode': None, if no error,
                'description': error discription or None if no error,
                'fileName': 'the name of the file returned',
                'fileToBytes': file content in bytes which is ready for storing in Odoo's Binary fields
            }
        :rtype: dict
        :raise requests.HTTPError: 
        """
        self.ensure_one()
        self._check_download_invoice_after_issued()
        if file_type not in SINVOICE_REPRESENTATION_FILETYPE:
            types_msg = "\n* %s;".join(SINVOICE_REPRESENTATION_FILETYPE)
            raise ValidationError(_("The filetype for S-Invoice representation file %s is not supported. It should be either:\n%s")
                                  % (file_type, types_msg))

        request_data = {
            'supplierTaxCode': self.company_id.vat,
            'invoiceNo': self.legal_number,
            'templateCode': self._get_sinvoice_template_name(),
            'fileType': file_type
        }
        auth = self.company_id.get_sinvoice_auth_str()
        req = requests.post(
            self.company_id.get_sinvoice_presentation_file_url(),
            data=json.dumps(request_data),
            headers={"Content-type": "application/json; charset=utf-8"},
            timeout=SINVOICE_TIMEOUT,
            auth=auth
            )
        # Raises :class:`HTTPError`, if one occurred.
        req.raise_for_status()
        data = req.json()
        return data

    def get_sinvoice_representation_files(self):
        self.ensure_one()
        update_vals = {}
        attachments = []
        generate_attachment = self.company_id.sinvoice_representation_file_as_attachment or self._context.get('force_sinvoice_representation_file_as_attachment', False)
        try:
            for file_type in SINVOICE_REPRESENTATION_FILETYPE:
                data = self._get_sinvoice_presentation_data(file_type)
                file_type = file_type.lower()
                filename = '%s.%s' % (data['fileName'], file_type)
                file_content = data['fileToBytes']
                if data['errorCode']:
                    raise UserError("%s: %s" % (data['errorCode'], data['description']))
                update_vals.update({
                    'sinvoice_representation_%s' % file_type: file_content,
                    'sinvoice_representation_filename_%s' % file_type: filename
                    })
                # if the company wants attachment
                if generate_attachment:
                    req_content = base64.decodebytes(file_content.encode())
                    attachment = (filename, req_content)
                    attachments.append(attachment)

            message = _("Successfully downloaded representation versions of the S-Invoice from the S-Invoice system.")
            if not generate_attachment:
                message += _("\nYou will be able to find the in the tab S-Invoice of the invoice form view above.")

        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
            message = _("Something went wrong while downloading the Representation version of the S-Invoice. Here is the debugging information:\n%s") % str(content)
        if update_vals:
            self.write(update_vals)
        if self._context.get('log_einvoice_message', False):
            self.message_post(body=message, attachments=attachments or None)
        return update_vals
    
    def get_einvoice_representation_files(self):
        if (
            self.sinvoice_transactionid
            and (not self.sinvoice_representation_pdf
                 or not self.sinvoice_representation_zip
                 or self._context.get('refresh_sinvoice_representation_file', False)
                 )
        ):
            self.get_sinvoice_representation_files()
        return super(AccountMove, self).get_einvoice_representation_files()
    
    # TODO: need to improve in odoo 14
    def _ensure_sinvoice_representation_files(self, retries=0, sleep=3):
        """
        This method is to ensure representation files available

        :param retries: number of times to retry. SInvoice may not have these information right after issuing invoice
        :param sleep: number of second to wait before retrying

        :return: dictionary of representation files in pdf and zip formats
        :rtype: dict
        
        :raise MissingError: when no file available in S-Invoice system to get
        """
        self.ensure_one()
        if not self.sinvoice_representation_pdf or not self.sinvoice_representation_zip or self._context.get('refresh_sinvoice_representation_file', False):
            self.get_sinvoice_representation_files()
        data = {
            'pdf': self.sinvoice_representation_pdf,
            'zip': self.sinvoice_representation_zip
            }
        if not data['pdf'] or not data['zip']:
            if retries > 0:
                retries -= 1
                time.sleep(sleep)
                return self._ensure_sinvoice_representation_files(retries)
            else:
                raise MissingError(_("No representation files avaiable yet. Please wait for a few minutes before trying again!"))
        else:
            return data

    def _get_exchange_user(self):
        return self.company_id.sinvoice_conversion_user_id or self.env.user

    def _get_sinvoice_exchange_data(self):
        """
        This method will connect S-Invoice and request for exchange data that could be used for conversion purpose
        
        :return: dictionary of return data
            {
                'errorCode': None, if no error,
                'description': error discription or None if no error,
                'fileName': 'the name of the file returned',
                'fileToBytes': file content in bytes which is ready for storing in Odoo's Binary fields
            }
            error code
            ----------
            200 OK, Success
            201 Created, Success of a resource creation when using the POST method
            400 Bad Request, The request parameters are incomplete or missing
            403 Forbidden, The action or the request URI is not allowed by the system
            404 Not Found, The resource referenced by the URI was not found
            422 Unprocessable Entity, One of the requested action has generated an error
            429 Too Many Requests, Your application is making too many requests and is being rate limited
            500 Internal Server Error, Used in case of time out or when the request, otherwise correct, was not able to complete.

        :rtype: dict
        :raise requests.HTTPError: 
        """
        self.ensure_one()
        self._check_download_invoice_after_issued()
        
        req_path = self.company_id.get_sinvoice_exchange_file_url()
        auth = self.company_id.get_sinvoice_auth_str()
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        request_data = {
            'supplierTaxCode' : self.company_id.vat,
            'templateCode': self._get_sinvoice_template_name(),
            'invoiceNo' : self.legal_number,
            'strIssueDate' : self._prepare_sinvoice_strIssueDate(),
            'exchangeUser' : self._get_exchange_user().name,
            }
        req = requests.post(
            req_path,
            data=request_data,
            headers=headers,
            timeout=SINVOICE_TIMEOUT,
            auth=auth
            )
        req.raise_for_status()
        data = req.json()
        return data

    def get_sinvoice_exchange_files(self):
        self.ensure_one()
        update_vals = {}
        attachments = []
        try:
            data = self._get_sinvoice_exchange_data()
            if data['errorCode']:
                if data['errorCode'] == 'INVOICE_NOT_FOUND':
                    message = _("The Invoice %s was not found for conversion. If the invoice has just been issued, you may need to wait"
                                " for a few minutes for the S-Invoice system to get it available for your query.") % self.legal_number
                else:
                    message = _("Could not download S-Invoice Converted file.\nError Code: %s\nError Description: %s") % (
                        data['errorCode'],
                        data['description']
                        )
            else:
                filename = '%s.pdf' % data['fileName']
                file_content = data['fileToBytes']
                update_vals.update({
                    'sinvoice_converted_file': file_content,
                    'sinvoice_converted_filename': filename
                    })
                message = _("Successfully downloaded the converted version of the S-Invoice from the S-Invoice system.")

                # if the company wants attachment
                if self.company_id.sinvoice_exchange_file_as_attachment or self._context.get('force_sinvoice_exchange_file_as_attachment', False):
                    req_content = base64.decodebytes(file_content.encode())
                    attachment = (filename, req_content)
                    attachments.append(attachment)
                else:
                    message += _("\nYou will be able to find it in the tab S-Invoice of the invoice form view above.")

        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
            message = _("Something went wrong while downloading S-Invoice Exchange/Converted invoice. Here is debugging information:\n%s") % str(content)

        if update_vals:
            self.write(update_vals)
        if self._context.get('log_einvoice_message', False):
            self.message_post(body=message, attachments=attachments or None)
        return update_vals
    
    def get_einvoice_converted_files(self):
        if (
            self.sinvoice_transactionid
            and (not self.sinvoice_converted_file
                 or self._context.get('refresh_sinvoice_converted_file', False)
                )
        ):
            self.get_sinvoice_exchange_files()
        return super(AccountMove, self).get_einvoice_converted_files()
    
    #todo: need to improve in odoo 14
    def _ensure_sinvoice_converted_file(self, retries=0, sleep=3):
        """
        This method is to ensure converted file available

        :param retries: number of times to retry. SInvoice may not have these information right after issuing invoice
        :param sleep: number of second to wait before retrying

        :return: converted file in binary
        :rtype: bytes
        
        :raise MissingError: when no file available in S-Invoice system to get
        """
        self.ensure_one()
        if not self.sinvoice_converted_file or self._context.get('refresh_sinvoice_converted_file', False):
            self.get_sinvoice_exchange_files()

        if not self.sinvoice_converted_file:
            if retries > 0:
                retries -= 1
                time.sleep(sleep)
                return self._ensure_sinvoice_converted_file(retries)
            else:
                raise MissingError(_("No converted file avaiable yet. Please wait for a few minutes before trying again!"))
        else:
            return self.sinvoice_converted_file

    def _get_sinvoice_taxpercentage(self):
        self.ensure_one()
        notax_line_ids = self.invoice_line_ids.filtered(lambda r: r.display_type == False and not r.tax_ids)
        invoice_tax_ids = self.invoice_line_ids.mapped('tax_ids')
        if not notax_line_ids and len(invoice_tax_ids) == 1:
            if invoice_tax_ids.amount_type == 'percent':
                return invoice_tax_ids[0].amount
        return (self.amount_tax / self.amount_untaxed) * 100

    def _prepare_sinvoice_payments_data(self):
        # TODO: find all related payments and there methods to fill here
        return [
            {
                # Tên phương thức thanh toán. Có thể nhập giá trị tùy ý.
                'paymentMethodName': 'TM/CK',
                }
            ]

    def _prepare_sinvoice_tax_breakdowns(self):
        tax_groups = []
        exemption_group = self.env.ref('l10n_vn_c200.tax_group_exemption').id
        invoice_tax = self._prepare_invoice_tax_data()

        # prepare 'taxBreakdowns' data to send to S-invoice
        for tax_line in invoice_tax:
            if tax_line['tax_group_id'] == exemption_group:
                tax_groups.append({
                    'taxPercentage': -2,
                    'taxableAmount': self.currency_id.round(tax_line['amount']),
                    'taxAmount': 0
                    })
            else:
                tax_groups.append({
                        'taxPercentage': tax_line['percent'],
                        'taxableAmount': self.currency_id.round(tax_line['amount']),
                        'taxAmount': self.currency_id.round(tax_line['amount_tax'])
                    })
        return tax_groups

    def _prepare_sinvoice_data(self):
        """
        Hook method that prepare data to send to S-Invoice for issuing new invoice there

        :return: the data to post to S-Invoice for invoice issuing according to the
            instructions here: https://sinvoice.viettel.vn/download/soft/tl_mo_ta_webservice_hoadondientu_doitac.doc
        :rtype: dict
        """

        date = self._get_sinvoice_date()
        # there could be a reason that cause the access_token is empty. E.g. due to wrong migration
        self._portal_ensure_token()

        ####################################################
        # Trạng thái điều chỉnh hóa đơn:
        # '1': Hóa đơn gốc
        # '3': Hóa đơn thay thế
        # '5': Hóa đơn điều chỉnh (dự kiến sẽ bỏ theo NĐ119)
        ####################################################
        general_invoice_info = {
            # ID để kiểm trùng giao dịch lập hóa đơn, là duy nhất với mỗi hóa đơn.
            # Với mỗi transactionUuid, khi đã gửi một transactionUuid với một hóa
            # đơn A thì mọi request lập hóa đơn với cùng transactionUuid sẽ trả về
            # hóa đơn A chứ không lập hóa đơn khác. Thời gian hiệu lực của
            # transactionUuid là 3 ngày.
            'transactionUuid': self.access_token,
            # Tên người lập hóa đơn. Nếu không truyền sang, hệ thống sẽ tự động lấy user được dùng để xác thực để lưu vào.
            'userName': self._get_issuing_user().name,
            'currencyCode': self.currency_id.name,
            # Số ký tự tối đa của tỷ giá là 13, trừ đi phần nguyên và dấu `,` nên sẽ làm tròn phần thập phân thành 7 ký tự
            # để đảm bảo đúng định dạng yêu cầu.
            'exchangeRate': float_round((1 / self.currency_id.with_context(date=date).rate),
                                        precision_digits=7),
            'invoiceSeries': self._get_account_sinvoice_serial_name(),
            'templateCode': self._get_sinvoice_template_name(),
            'invoiceType': self._get_account_sinvoice_type_name(),
            # ngày phát hành hoá đơn không được phép lớn hơn ngày hiện tại và nhỏ hơn ngày của hoá đơn đã phát hành trước đó.
            # Trong trường hợp không gửi ngày lập sang, hệ thống tự động lấy theo thời gian hiện tại trên hệ thống với múi giờ GMT+7
            # 'invoiceIssuedDate': int(datetime.datetime.timestamp(date) * 1000),
            'adjustmentType': '1',
            # Trạng thái thanh toán của hóa đơn
            # True: Đã thanh toán
            # False: Chưa thanh toán
            'paymentStatus': True if self.invoice_payment_state == 'paid' else False,
            'paymentType': 'TM/CK',
            'paymentTypeName': 'TM/CK',
            # Cho khách hàng xem hóa đơn trong Quản lý hóa đơn
            'cusGetInvoiceRight': True,
        }
        # if self.einvoice_api_version == 'v2':
        #     general_invoice_info.update({
        #         'specialNote': self.narration or ''
        #     })
        total_in_word = self.total_in_word
        if self._einvoice_need_english():
            total_in_word += " (%s)" % self.currency_id.with_context(lang='en_US').amount_to_text(self.amount_total)

        summarize_info = {
            'sumOfTotalLineAmountWithoutTax': self.amount_untaxed,
            'totalAmountWithoutTax': self.amount_untaxed,
            'totalTaxAmount': self.amount_tax,
            'totalAmountWithTax': self.amount_total,
            'totalAmountWithTaxInWords': total_in_word,
            'discountAmount': 0,
            'taxPercentage': self._get_sinvoice_taxpercentage()
        }

        if self.type == 'out_refund':
            general_invoice_info.update({
                'adjustmentType': '5',
                'adjustmentInvoiceType': 1,
                'originalInvoiceId': self.reversed_entry_id.legal_number,
                'originalInvoiceIssueDate': fields.Date.to_string(self.reversed_entry_id.einvoice_invoice_date),
                'additionalReferenceDesc': self._context.get('additionalReferenceDesc', ''),
                'additionalReferenceDate': fields.Date.to_string(date),
            })
            summarize_info.update({
                'isTotalAmountPos': False,
                'isTotalTaxAmountPos': False,
                'isTotalAmtWithoutTaxPos': False,
                'isDiscountAmtPos': False
            })
        return {
            'generalInvoiceInfo': general_invoice_info,
            'payments': self._prepare_sinvoice_payments_data(),
            'buyerInfo': {
                'buyerName': self.partner_id.name if self.partner_id.name and self.partner_id.name != self.partner_id.commercial_company_name else '',
                'buyerLegalName': self.commercial_partner_id.name,
                'buyerTaxCode': '' if self._einvoice_need_english() else self.commercial_partner_id.vat or '',
                'buyerAddressLine': self._get_cusomter_invoice_address()._einvoice_display_address(),
                'buyerCityName': self.commercial_partner_id.city or self.commercial_partner_id.state_id.name or '',
                'buyerCountryCode': self.commercial_partner_id.country_id and self.commercial_partner_id.country_id.code or '',
                'buyerPhoneNumber': self.commercial_partner_id.phone and self._phone_format(self.commercial_partner_id.phone) or '',
                'buyerEmail': self._get_cusomter_invoice_address().email or self.commercial_partner_id.email or '',
               },
            'sellerInfo': {
                'sellerLegalName': self._prepare_einvoice_seller_legal_name(),
                'sellerTaxCode': self.company_id.vat or '',
                'sellerAddressLine': self.company_id.partner_id._einvoice_display_address(),
                'sellerPhoneNumber': self.company_id.phone or '',
                'sellerEmail': self.company_id.email and self.company_id.email.strip() or '',
                'sellerBankName': self._prepare_sinvoice_seller_bank()['bank_name'],
                'sellerBankAccount': self._prepare_sinvoice_seller_bank()['bank_account'],
                'sellerWebsite': self.company_id.website or '',
               },
            'itemInfo': self.invoice_line_ids._prepare_einvoice_lines_data(),
            'summarizeInfo': summarize_info,
            'taxBreakdowns': self._prepare_sinvoice_tax_breakdowns()
            }

    def _prepare_update_vals_after_issuing(self, returned_vals):
        """
        This method inherit from the corresponding method in to_einvoice_common model
 
        @param returned_vals: the result that returned by S-Invoice system after issuing the invoice
        @return: dictionary of values to update the current invoice after issuing
        @rtype: dict
        """
        
        res = super(AccountMove, self)._prepare_update_vals_after_issuing(returned_vals)
        if self.company_einvoice_provider == 'sinvoice':
            res.update({
                'sinvoice_transactionid': returned_vals['result']['transactionID'],
                'legal_number': returned_vals['result']['invoiceNo'],
                'sinvoice_reservation_code': returned_vals['result']['reservationCode'],
                'account_sinvoice_serial_id': self.journal_id.get_account_sinvoice_serial().id,
                'account_sinvoice_template_id': self.journal_id.get_sinvoice_template().id,
                'account_sinvoice_type_id':self.journal_id.get_account_sinvoice_type().id
                })
        return res

    def _issue_sinvoice(self, raise_error=True):
        self.ensure_one()

        #check invoice's information before issue
        self._check_general_infor()
        if self.company_einvoice_provider == 'sinvoice':
            self._check_invoice_date(self.company_id.sinvoice_start)

        # use new cursor to handle each invoice issuing
        # this could help commit a success issue before an error occurs that may roll back
        # the data in Odoo while the invoice is already available in S-Invoice database
        cr = registry(self._cr.dbname).cursor()
        self = self.with_env(self.env(cr=cr))

        auth_str = self.company_id.get_sinvoice_auth_str()
        error = False
        try:
            req = requests.post(
                self.company_id.get_sinvoice_create_url(),
                data=json.dumps(self._prepare_sinvoice_data()),
                headers={"Content-type": "application/json; charset=utf-8"},
                timeout=SINVOICE_TIMEOUT,
                auth=auth_str
                )

            req.raise_for_status()
            returned_vals = req.json()
            if returned_vals['errorCode']:
                error = True
                message = _("Could not issue S-Invoice from the invoice %s due to the error code `%s`.\n") % (self.name or self.legal_number, returned_vals['errorCode'])
                if returned_vals['errorCode'] == 'DONOT_HAVE_PERMISSION':
                    message += _("Your S-Invoice account has been disabled or you don't have enough permission. Please contact your Viettel"
                                 " S-Invoice agent for help.")
                elif returned_vals['errorCode'] == 'TEMPLATE_NOT_FOUND':
                    message += _("The template is invalid. Please specify a right S-Invoice template for the journal %s or the company %s."
                                 " You may need to register a template in S-Invoice system priorily.") % (self.journal_id.name, self.company_id.name)
                elif returned_vals['errorCode'] == 'INVOICE_ISSUED_DATE_INVALID':
                    message += _("The invoice date %s is invalid. Probably this date is earlier than the issue date of a previously issued invoice."
                                " You may fix this by modifying the invoice date to a later one.") % format_date(self.env, self.invoice_date)
                elif returned_vals['errorCode'] == 'INVOICE_ISSUED_DATE_OVER_CURRENT_TIME':
                    message += _("The invoice date must not be in the future. If you find it as the current date, this could be a problem"
                                 " in your timezone settings. You may fix this by modifying the invoice date to a date that is less than"
                                 " or equal to %s, or fixing your timezone.") % format_date(self.env, self.invoice_date)
                elif returned_vals['errorCode'] == 'OUT_OF_INVOICE_NO':
                    message += _("The possibility could be either:\n"
                                 "1. The S-Invoice template is not relevant to the S-Invoice Serial\n"
                                 "2. You have run out of your registered range of invoice numbers."
                                 " You may need to contact your Viettel S-Invoice agent for help.")
                elif returned_vals['errorCode'] == 'BUYER_PHONE_NUMBER_INVALID':
                    message += _("Invalid customer phone number %s") % self.commercial_partner_id.phone
                elif returned_vals['errorCode'] == 'ITEM_NAME_INVALID':
                    message += _("It seems that your product name/description was too long for SInvoice. You should shorten your product name/description to less than %s characters. ") % (self.journal_id.einvoice_item_name_limit)
                elif returned_vals['errorCode'] == 'ITEM_NAME_NULL':
                    message += _("An invoice line has no name / description. If you were sending product description to SInvoice, you may either reconfigure your "
                    "corresponding journal to use product name instead, or enter a description for this product.")
                else:
                    message += _(" Error: %s") % returned_vals['description']
            else:
                message = _("E-Invoice created on S-Invoice: Invoice No: %s") % (returned_vals['result']['invoiceNo'])
                self.write(self._prepare_update_vals_after_issuing(returned_vals))
        except requests.HTTPError as e:
            error = True
            message = _("Something went wrong when issuing E-Invoice. Here is the debugging information:\n%s") % str(e)
        if error and raise_error:
            cr.rollback()
            cr.close()
            raise ValidationError(message)
        self.message_post(body=message)
        cr.commit()
        cr.close()
        return error

    # Inherit method
    def _issue_einvoice(self,raise_error):
        res = super(AccountMove, self)._issue_einvoice(raise_error)
        if self.company_einvoice_provider == 'sinvoice':
            self._issue_sinvoice(raise_error)
        return res

    def _sinvoice_unpaid(self, raise_error=True):
        """
        This method will connect the S-Invoice system and set the status of the corresponding S-Invoice to Paid
        """
        self.ensure_one()
        auth_str = self.company_id.get_sinvoice_auth_str()
        req_data = {
            'supplierTaxCode': self.company_id.vat,
            'invoiceNo': self.legal_number,
            'strIssueDate': self._prepare_sinvoice_strIssueDate(),
            }
        error = False
        update_vals = {}
        try:
            req = requests.post(
                self.company_id.get_sinvoice_cancel_payment_status_url(),
                data=req_data,
                headers={"Content-type": "application/x-www-form-urlencoded; charset=utf-8"},
                timeout=SINVOICE_TIMEOUT,
                auth=auth_str
                )
            req.raise_for_status()
            content = req.json()
            if content['errorCode'] and content['errorCode'] != 'NO_RECORD_UPDATED':
                message = _("Could not set the corresponding S-Invoice as Issued and not Paid. Error Code: %s.\nError Description: %s") % (content['errorCode'], content['description'])
                error = True
            elif content['errorCode'] == 'NO_RECORD_UPDATED':
                message = _("The S-Invoice seemed to be turned into the status Issued and not Paid previously. Error Code: %s.\nError Description: %s") % (content['errorCode'], content['description'])
                if self.einvoice_state != 'issued':
                    update_vals.update({
                        'einvoice_state': 'issued',
                        })
            else:
                message = _("The corresponding S-Invoice %s has been set as Unpaid in S-Invoice system.") % self.legal_number
                update_vals.update({
                    'einvoice_state': 'issued',
                    })
        except requests.HTTPError as e:
            error = True
            message = _("Could not set the S-Invoice %s as Issued and not Paid.") % self.legal_number
            if e.response.status_code == 500:
                message += _(" You might have not configured allowed IPs in your S-Invoice portal to grant access from your Odoo instance's IP."
                             " Or there could be something wrong with your S-Invoice's username and/or password.")
            else:
                message += _(" Here is the debugging information:\n%s") % str(e)
        if error and raise_error:
            raise ValidationError(message)
        if update_vals:
            self.write(update_vals)
        self.message_post(body=message)

    def action_sinvoice_unpaid(self):
        for r in self:
            r._sinvoice_unpaid()

    def _write(self, vals):
        res = super(AccountMove, self)._write(vals)
        invoice_payment_state = vals.get('invoice_payment_state', False)
        if invoice_payment_state and invoice_payment_state != 'paid':
            for r in self.filtered(lambda inv: inv.einvoice_state == 'paid' and inv.company_id.sinvoice_synch_payment_status and inv.sinvoice_transactionid):
                r._sinvoice_unpaid()
        return res

    def _sinvoice_paid(self, raise_error=True):
        """
        This method will connect the S-Invoice system and set the status of the corresponding S-Invoice to Paid
        """
        self.ensure_one()
        auth_str = self.company_id.get_sinvoice_auth_str()
        req_data = {
            'supplierTaxCode': self.company_id.vat,
            'invoiceNo': self.legal_number,
            'strIssueDate': self._prepare_sinvoice_strIssueDate(),
            # mặc dùng trong tài liệu có nói paymentType không còn sử dụng và thay bằng paymentMethodName như thực tế không phải vậy
            'paymentType': 'CK',
            # mặc dùng trong tài liệu có nói paymentTypeName không còn sử dụng và thay bằng paymentMethodName như thực tế không phải vậy
            'paymentTypeName': 'CK',
            'paymentMethodName': 'CK',
            'cusGetInvoiceRight': True,
            # mặc dùng trong tài liệu không nói là phải truyền templateCode nhưng ko truyền thì lỗi
            'templateCode': self._get_sinvoice_template_name(),
            }
        error = False
        update_vals = {}
        try:
            req = requests.post(
                self.company_id.get_sinvoice_update_payment_status_url(),
                data=req_data,
                headers={"Content-type": "application/x-www-form-urlencoded; charset=utf-8"},
                timeout=SINVOICE_TIMEOUT,
                auth=auth_str
                )
            req.raise_for_status()
            content = req.json()
            if content['errorCode'] and content['errorCode'] != 'INVOICE_PAID':
                message = _("Could not set the corresponding S-Invoice as Paid. Error Code: %s.\nError Description: %s") % (content['errorCode'], content['description'])
                error = True
            elif content['errorCode'] == 'INVOICE_PAID':
                message = _("The S-Invoice %s has been set as Paid in S-Invoice system already.") % self.legal_number
                if self.einvoice_state != 'paid':
                    update_vals.update({
                        'einvoice_state': 'paid',
                        })
            else:
                message = _("The corresponding S-Invoice %s has been set as Paid in S-Invoice system.") % self.legal_number
                update_vals.update({
                    'einvoice_state': 'paid',
                    })
        except requests.HTTPError as e:
            error = True
            message = _("Could not set the S-Invoice %s as Paid.") % self.legal_number
            if e.response.status_code == 500:
                message += _(" You might have not configured allowed IPs in your S-Invoice portal to grant access from your Odoo instance's IP."
                             " Or there could be something wrong with your S-Invoice's username and/or password.")
            else:
                message += _(" Here is the debugging information:\n%s") % str(e)
        if error and raise_error:
            raise ValidationError(message)
        if update_vals:
            self.write(update_vals)
        self.message_post(body=message)

    def action_sinvoice_paid(self):
        for r in self:
            r._sinvoice_paid()

    def action_invoice_paid(self):
        super(AccountMove, self).action_invoice_paid()
        for r in self.filtered(lambda inv: inv.invoice_payment_state == 'paid' and inv.einvoice_state == 'issued' and inv.company_id.sinvoice_synch_payment_status and inv.sinvoice_transactionid):
            r._sinvoice_paid()

    def _cancel_sinvoice(self, raise_error=True):
        self.ensure_one()
        if self.einvoice_state in ('not_issued', 'cancelled'):
            raise UserError(_("The S-Invoice corresponding to the invoice %s could not be cancelled because"
                              " it has not been issued or cancelled aready.")
                              % self._name)
        auth_str = self.company_id.get_sinvoice_auth_str()
        additional_ref_date = self._context.get('additionalReferenceDate', fields.Datetime.now())
        # S-Invoice uses UTC+7
        additional_ref_date_utc7 = self.env['to.base'].convert_utc_time_to_tz(additional_ref_date, tz_name='Asia/Ho_Chi_Minh')

        req_data = {
            'supplierTaxCode': self.company_id.vat,
            'templateCode': self._get_sinvoice_template_name(),
            'invoiceNo': self.legal_number,
            'strIssueDate': self._prepare_sinvoice_strIssueDate(),
            # Tên văn bản thỏa thuận hủy hóa đơn
            'additionalReferenceDesc': self._context.get('additionalReferenceDesc'),
            # Ngày thỏa thuận huỷ hoá đơn, không vượt quá ngày hiện tại
            'additionalReferenceDate': additional_ref_date_utc7.strftime('%Y%m%d%H%M%S'),
            }
        error = False
        # use new cursor to handle each invoice cancel
        # this could help commit a success cancel action before an error occurs that may roll back
        # the data in Odoo while the invoice is already cancel in S-Invoice database
        cr = registry(self._cr.dbname).cursor()
        self = self.with_env(self.env(cr=cr))
        try:
            req = requests.post(
                self.company_id.get_sinvoice_cancel_url(),
                data=req_data,
                headers={"Content-type": "application/x-www-form-urlencoded; charset=utf-8"},
                timeout=SINVOICE_TIMEOUT,
                auth=auth_str
                )
            req.raise_for_status()
            content = req.json()
            if content['errorCode']:
                message = _("Could not cancel the E-invoice %s in S-Invoice system. Error: %s") % (self.legal_number or self.name, content['description'])
                error = True
            else:
                message = _("The legal E-Invoice %s has been cancelled on S-Invoice.") % self.legal_number
                self.write({
                    'einvoice_state': 'cancelled',
                    'einvoice_cancellation_date': additional_ref_date
                    })
                self.with_context(
                    refresh_sinvoice_representation_file=True
                ).get_einvoice_representation_files()
                self.with_context(
                    refresh_sinvoice_converted_file=True
                ).get_einvoice_converted_files()
        except requests.HTTPError as e:
            error = True
            message = _("Could not cancel the S-Invoice %s.") % self.legal_number
            if e.response.status_code == 500:
                message += _(" You might have not configured allowed IPs in your S-Invoice portal to grant access from your Odoo instance's IP."
                             " Or there could be something wrong with your S-Invoice's username and/or password.")
        if error and raise_error:
            cr.rollback()
            cr.close()
            raise ValidationError(message)
        self.message_post(body=message)
        cr.commit()
        cr.close()

    def _get_report_base_filename(self):
        self.ensure_one()
        if self.journal_id.einvoice_send_mail_option == 'converted':
            name = self.sinvoice_converted_filename
        else:
            name = self.sinvoice_representation_filename_pdf
        if self.type in self.get_sale_types() and self.einvoice_state != 'not_issued' and name:
            name = '.'.join(name.split('.')[:-1])
            return _("Invoice - %s") % name
        else:
            return super(AccountMove, self)._get_report_base_filename()

    def _invoice_to_issue_einvoice(self):
        res = super(AccountMove, self)._invoice_to_issue_einvoice()
        return res.filtered(lambda move: move.invoice_date >= move.company_id.sinvoice_start if move.company_einvoice_provider == 'sinvoice' else True)

    def action_sync_sinvoice_status(self):
        for r in self:
            if (
                r.einvoice_state not in ('issued', 'paid', 'adjusted')
                or not r.sinvoice_transactionid
                or not r.access_token
            ):
                continue
            api_url = r.company_id.get_sinvoice_search_by_transaction_uuid_url()
            with r.env.cr.savepoint():
                try:
                    req = requests.post(
                        api_url,
                        data={'supplierTaxCode': r.company_id.vat, 'transactionUuid': r.access_token},
                        headers={"Content-type": "application/x-www-form-urlencoded; charset=utf-8"},
                        timeout=SINVOICE_TIMEOUT,
                        auth=r.company_id.get_sinvoice_auth_str(),
                        )
                    req.raise_for_status()
                    returned_vals = req.json()
                    status = returned_vals.get('result', [{}])[0].get('status', '')
                    if status == 'Hóa đơn xóa bỏ':
                        r.write({'einvoice_state': 'cancelled'})
                        r.with_context(
                            refresh_sinvoice_representation_file=True
                        ).get_einvoice_representation_files()
                        r.with_context(
                            refresh_sinvoice_converted_file=True
                        ).get_einvoice_converted_files()
                except requests.HTTPError as e:
                    content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
                    raise UserError(_("Something went wrong when synchronizing status for the E-Invoice %s. Here is the debugging information:\n%s") % (r.legal_number, str(content)))

    @api.model
    def _cron_ensure_einvoice_download_file(self):
        invoices = self.env['account.move'].search([('einvoice_state', '!=', 'not_issued'),('sinvoice_transactionid', '!=', False)])
        for invoice in invoices:
            try:
                invoice._ensure_sinvoice_representation_files()
                invoice._ensure_sinvoice_converted_file()
            except:
                continue
        return super(AccountMove, self)._cron_ensure_einvoice_download_file() 
