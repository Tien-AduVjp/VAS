import logging
import requests, json
import time
import base64
from dateutil.relativedelta import relativedelta

from odoo import models, api, fields, registry, _
from odoo.exceptions import UserError, ValidationError, MissingError
from odoo.tools import format_date, float_round

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    vninvoice_representation_pdf = fields.Binary(string='VN-invoice Representation File (PDF)', attachment=True,
                                                readonly=True, copy=False,
                                                help="The display version of the VN-invoice in PDF format")
    vninvoice_representation_filename_pdf = fields.Char(string='VN-invoice Representation Filename (PDF)', readonly=True,
                                                       copy=False)
    vninvoice_representation_xml = fields.Binary(string='VN-Invoice Representation File (XML)', attachment=True, readonly=True, copy=False,
                                                 help="The display version of the VN-Invoice in XML format.")
    vninvoice_representation_filename_xml = fields.Char(string='VN-Invoice Representation Filename (XML)', readonly=True, copy=False)
    vninvoice_converted_file = fields.Binary(string='VN-Invoice Converted File', attachment=True, readonly=True, copy=False)
    vninvoice_converted_filename = fields.Char(string='VN-Invoice Converted Filename', readonly=True, copy=False)
    # TODO: fields above will be moved to einvoice_common in odoo14
    vninvoice_transactionid = fields.Char(string='VN-invoice Transaction ID', copy=False, readonly=True,
                                         help="Technical field to store transaction ID that was returned by VN-invoice after invoice creation.")
    check_vninvoice_approved_and_signed = fields.Boolean(default=False, copy=False, readonly=True, 
                                                        help="This field is to check whether the invoice is signed or not. "
                                                            "In the case that api to sign is failed, a button will appear after issuing the invoice"
                                                            "to sign the invoice again")
    account_vninvoice_serial_id = fields.Many2one('account.vninvoice.serial', string='VN-Invoice Serial', copy=False, readonly=True, ondelete='restrict')
    account_vninvoice_template_id = fields.Many2one('account.vninvoice.template', string='VN-Invoice Template', copy=False, readonly=True, ondelete='restrict')
    account_vninvoice_type_id = fields.Many2one('account.vninvoice.type', string='VN-Invoice Type', copy=False, readonly=True, ondelete='restrict')
    vninvoice_recordid = fields.Char(string='VN-Invoice ID', readonly=True, copy=False, help="Technical field to store record ID that was returned by VN-invoice after invoice creation.")
    einvoice_api_version = fields.Selection(related='company_id.einvoice_api_version')

    def action_invoice_paid(self):
        super(AccountMove, self).action_invoice_paid()
        for r in self.filtered(lambda inv: inv.invoice_payment_state == 'paid' and inv.einvoice_state == 'issued' and inv.vninvoice_transactionid):
            r.einvoice_state = 'paid'

    def _get_account_vninvoice_serial_name(self):
        """
        Return the name of the vninvoice serial. For example, 'AA/18E', 'AA/19E'
        :rtype: string
        """
        if self.account_vninvoice_serial_id:
            return self.account_vninvoice_serial_id.name
        else:
            return self.journal_id.get_account_vninvoice_serial().name

    def _get_vninvoice_template_name(self):
        """
        Return the name of the vninvoice template. For example, '01GTKT0/001', '01GTKT0/002'
        :rtype: string
        """
        if self.account_vninvoice_template_id:
            return self.account_vninvoice_template_id.name
        else:
            return self.journal_id.get_vninvoice_template().name
    
    def _get_payment_date(self):
        """
        Return the date of invoice date if payment date does not exist
        :rtype: Date
        """
        payment_ids = self.env['account.payment'].search([('invoice_ids', '=',self.id)])
        return min(payment_ids.mapped('payment_date')) if payment_ids.mapped('payment_date') else self.invoice_date
        
    def _prepare_vninvoice_tax_breakdowns(self):
        # prepare 'taxBreakdowns' data to send to VN-invoice
        tax_groups = []
        exemption_group = self.env.ref('l10n_vn_c200.tax_group_exemption').id
        invoice_tax = self._prepare_invoice_tax_data()
        if self.einvoice_api_version == 'v1' and self.type == 'out_refund':
            origin_invoice_tax = self.reversed_entry_id._prepare_invoice_tax_data()
            for origin_tax_line in origin_invoice_tax:
                if origin_tax_line['tax_group_id'] == exemption_group:
                    tax_groups.append({
                        'vatPercent': -1,  # value of tax exemption in vninvoice is -1
                        'name': origin_tax_line['name'],
                        'vatAmount': 0
                        })
                else:
                    vat_amount = origin_tax_line['amount_tax']
                    tax_lines = filter(lambda r: r['percent'] == origin_tax_line['percent'], invoice_tax)
                    for tax_line in tax_lines:
                        vat_amount -= tax_line['amount_tax']
                        invoice_tax.remove(tax_line)
                    tax_groups.append({
                        'vatPercent': int(origin_tax_line['percent']),
                        'name': origin_tax_line['name'],
                        'vatAmount': self.currency_id.round(vat_amount)
                    })
        for tax_line in invoice_tax:
            value = {}
            if tax_line['tax_group_id'] == exemption_group:
                tax_groups.append({
                    'vatPercent': -1,  # value of tax exemption in vninvoice is -1
                    'name': tax_line['name'],
                    'vatAmount': 0
                })
            else:
                amount_tax = self.currency_id.round(tax_line['amount_tax'])
                tax_groups.append({
                    'vatPercent': int(tax_line['percent']),
                    'name': tax_line['name'],
                    'vatAmount': amount_tax if self.type == 'out_invoice' or self.einvoice_api_version == 'v2' else - amount_tax
                })
        return tax_groups

    def _prepare_vninvoice_data(self):
        """
        Hook method that prepare data to send to VN-invoice for issuing new invoice there

        :return: the data to post to VN-Invoice for invoice issuing
        :rtype: dict
        """

        #  there could be a reason that cause the access_token is empty. E.g. due to wrong migration
        self._portal_ensure_token()
        data = {
            'invoiceDate': fields.Date.to_string(self.invoice_date),
            'userNameCreator': self._get_issuing_user().name,
            'invoiceDetails': self.invoice_line_ids._prepare_einvoice_lines_data(),
            'invoiceTaxBreakdowns': self._prepare_vninvoice_tax_breakdowns(),
            'Note': self.narration or '',
            'paymentMethod': 'Tiền mặt hoặc chuyển khoản',
            'totalAmount': float_round(self.amount_untaxed, precision_digits=2),
            'totalVatAmount': float_round(self.amount_tax, precision_digits=2),
            'totalPaymentAmount': float_round(self.amount_total, precision_digits=2),
            'exchangeRate': float_round((1 / self.currency_id.with_context(date=self.invoice_date).rate),
                                        precision_digits=4),
            'paymentDate': self._get_payment_date().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            'buyerEmail': self._get_cusomter_invoice_address().email or self.commercial_partner_id.email or '',
            'buyerFullName': self.commercial_partner_id.name,
            'buyerLegalName': self.partner_id.name if self.partner_id.name and self.partner_id.company_type == 'person' else '',
            'buyerTaxCode': '' if self._einvoice_need_english() else self.commercial_partner_id.vat or '',
            'buyerAddressLine': self._get_cusomter_invoice_address()._einvoice_display_address(),
            'buyerDistrictName': '',
            'buyerCityName': self.commercial_partner_id.city or self.commercial_partner_id.state_id.name or '',
            'buyerCountryCode': self.commercial_partner_id.country_id and self.commercial_partner_id.country_id.code or '',
            'buyerPhoneNumber': self.commercial_partner_id.phone and self._phone_format(
                self.commercial_partner_id.phone) or '',
            'buyerFaxNumber': '',
            'buyerBankName': '',
            'buyerBankAccount': '',
            # Mã đơn hàng / hợp đồng / mã tra cứu
            'idBuyer': str(self.commercial_partner_id.id) or '',
            'buyerGroupCode': '',
            'buyerCode': str(self.commercial_partner_id.id) or '',
            'idBuyerGroup': '',
            'buyerGroupName': '',
            'currency': self.currency_id.name,
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
        if self.type == 'out_refund':
            issued_refunds = self.env['account.move'].search(
                [('reversed_entry_id', '=', self.reversed_entry_id.id), ('einvoice_state', '!=', 'not_issued')])
            if issued_refunds:
                raise UserError(
                    _("You cannot issue this credit note because VN-invoice system only allow to issue one adjustment invoice for an original invoice. "
                      "The original invoice of invoice %s has have one adjustment invoice %s.") % (self.reversed_entry_id.display_name, issued_refunds[0].display_name))
            if self.einvoice_api_version == 'v1':
                data.update({
                    'idReference': self.reversed_entry_id.vninvoice_transactionid,
                    'totalAmount': float_round(self.reversed_entry_id.amount_untaxed - self.amount_untaxed, precision_digits=2),
                    'totalVatAmount': float_round(self.reversed_entry_id.amount_tax - self.amount_tax, precision_digits=2),
                    'totalPaymentAmount': float_round(self.reversed_entry_id.amount_total - self.amount_total, precision_digits=2),
                    'recordNo': self._context.get('additionalReferenceDesc', ''),
                    'recordDate': fields.Date.to_string(self.invoice_date),
                    'fileOfRecord': self.adjustment_record and self.adjustment_record.decode('UTF-8') or '',
                    'fileNameOfRecord': self.adjustment_record_name or '',
                    'reason': self.ref
                })
            else:
                data.update({
                    'erpIdReference': self.reversed_entry_id.vninvoice_transactionid,
                })
        return [data] if self.type == 'out_invoice' else data
    
    def _find_issued_invoice_later(self):
        """
        This method finds the issued invoices later
        """
        self.ensure_one()
        domain = [
            ('type', '=', 'out_invoice'),
            ('einvoice_state', '!=', 'not_issued'),
            ('invoice_date', '>', self.invoice_date),
            ('journal_id.einvoice_enabled', '=', True),
            ('vninvoice_transactionid','!=', False)
        ]
        if self.company_id.vninvoice_start_date:
            domain.append(('invoice_date', '>', self.company_id.vninvoice_start_date))
        return self.env['account.move'].search(domain)

    def _prepare_update_vals_after_issuing(self, returned_vals):
        """
        This method inherit from the corresponding method in to_einvoice_common model
 
        @param returned_vals: the result that returned by VN-invoice system after issuing the invoice
        @return: dictionary of values to update the current invoice after issuing
        @rtype: dict
        """
        res = super(AccountMove, self)._prepare_update_vals_after_issuing(returned_vals)
        if self.company_einvoice_provider == 'vninvoice':
            res.update({
            'vninvoice_transactionid': self.access_token,
            'legal_number': returned_vals['invoiceNo'],
            'account_vninvoice_serial_id': self.journal_id.get_account_vninvoice_serial().id,
            'account_vninvoice_template_id': self.journal_id.get_vninvoice_template().id,
            'account_vninvoice_type_id': self.journal_id.get_account_vninvoice_type().id,
            'vninvoice_recordid': returned_vals['id']
        })
        return res

    def _issue_vninvoice(self, raise_error=True):
        self.ensure_one()
        # check invoice
        self._check_general_infor()
        if self.type == 'out_refund' and not self.reversed_entry_id.check_vninvoice_approved_and_signed:
            raise UserError(_("Original invoice %s has not been signed.") % self.reversed_entry_id.display_name)
        if self.company_einvoice_provider == 'vninvoice':
            self._check_invoice_date(self.company_id.vninvoice_start_date)
                                     
        if self.type == 'out_invoice' and self._find_issued_invoice_later():
            raise UserError(_("You cannot issue VN-invoice for the invoice %s dated %s because Issued E-invoices "
                              "with later invoice date are existing.")
                            % (
                                self.name or self.legal_number,
                                format_date(self.env, self.invoice_date),)
                            )

        if self.einvoice_api_version == 'v2' and self.type == 'out_refund':
            if self.reversed_entry_id.einvoice_error_notif_state == 'none':
                raise UserError(_("You must create and sign the e-invoice error notification of invoice %s before issuing this adjustment invoice") % self.reversed_entry_id.name)
            elif self.reversed_entry_id.einvoice_error_notif_state == 'draft':
                raise UserError(
                    _("You must sign the e-invoice error notification of invoice %s before issuing this adjustment invoice") % self.reversed_entry_id.name)

        # use new cursor to handle each invoice issuing
        # this could help commit a success issue before an error occurs that may roll back
        # the data in Odoo while the invoice is already available in VN-invoice database
        cr = registry(self._cr.dbname).cursor()
        self = self.with_env(self.env(cr=cr))
        error = False
        url = self.company_id.get_vninvoice_create_batch_url() if self.type == 'out_invoice' else self.company_id.get_vninvoice_invoice_adjustment()
        params = {}
        if self.einvoice_api_version == 'v2':
            params.update({
                'TemplateNo': int(self._get_vninvoice_template_name()),
                'serialNo': self._get_account_vninvoice_serial_name()
            })
        try:
            req = requests.post(
                url,
                json=self._prepare_vninvoice_data(),
                headers={"Content-type": "application/json",
                         "Authorization":"Bearer {}".format(self.company_id.get_vninvoice_api_token())},
                params=params
            )
            req.raise_for_status()
            returned_vals = json.loads(req.text)
            if not returned_vals['succeeded']:
                error = True
                message = _("Could not issue the E-invoice %s in VN-invoice system. Error: %s") % (self.legal_number or self.name, returned_vals['message'])
            else:
                data = returned_vals['data'][0] if self.type == 'out_invoice' else returned_vals['data']
                self.write(self._prepare_update_vals_after_issuing(data))
                message = _("E-Invoice created on VN-Invoice: Invoice No: %s") % (data['invoiceNo'])

        except requests.HTTPError as e:
            error = True
            content = e
            if e.response.status_code == 400:
                content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code).get('error', {}).get('details', '')
            message = _("Something went wrong when issuing E-Invoice. Here is the debugging information:\n%s") % str(content)
        if error and raise_error:
            cr.rollback()
            cr.close()
            raise ValidationError(message)
        self.message_post(body=message)
        cr.commit()
        cr.close()
        return error
    
    #api to approve and sign einvoice
    def action_approve_and_sign(self):
        self.ensure_one()

        # api to approve and sign invoice after issuing
        method_request = requests.patch if self.einvoice_api_version == 'v1' else requests.post
        try:
            req = method_request(
                self.company_id.get_vninvoice_approve_and_sign_url().format(self.vninvoice_transactionid),
                headers={"Content-type": "application/json",
                         "Authorization": "Bearer {}".format(self.company_id.get_vninvoice_api_token())}
            )
            req.raise_for_status()
            data = json.loads(req.text)
            if not data['succeeded']:
                message = _('Approve and Sign of The invoice %s is failed. Error: %s') % (self.name, data['message'])
            else:
                message = _('E-Invoice has been approved and signed successfully')
                self.check_vninvoice_approved_and_signed = True
        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
            message = _("Something went wrong when approve and sign the E-Invoice %s. Here is the debugging information:\n%s") % (self.legal_number, str(content))
        self.message_post(body=message)
    
    # Inherit method
    def _issue_einvoice(self,raise_error):
        res = super(AccountMove, self)._issue_einvoice(raise_error)
        if self.company_einvoice_provider == 'vninvoice':
            self._issue_vninvoice(raise_error)
            # TODO: Need improvement: This part should not be done automatically.
            # May adding an option in General Settings to enable this or not. Even if enabled,
            # we should update the right status after (may be 'approved' or 'signed'), depends
            # on the configurations on VN-Invoice system
            # if self.einvoice_state in ['issued','paid']:
                # self.action_approve_and_sign()
        return res

    def _get_unofficial_vninvoice(self):
        """
        this method allow to get data of E-invoice and then can convert it into PDF file
        :return:{'data':{'id':'string','data':'bytes'
        """
        self.ensure_one()
        self._check_download_invoice_after_issued()

        update_vals = {}
        attachments = []
        method_request = requests.get if self.einvoice_api_version == 'v1' else requests.post
        try:
            req = method_request(
                self.company_id.get_vninvoice_unofficial_url().format(self.vninvoice_transactionid),
                headers={"Content-type": "application/json",
                         "Authorization": "Bearer {}".format(self.company_id.get_vninvoice_api_token())}
                )
            req.raise_for_status()
            data = json.loads(req.text)
            if not data['succeeded']:
                message = _('Representation PDF file of the invoice %s be downloaded unsuccessfully. Error: %s') % (self.name,data['message'])
            else:
                filename = 'VNinvoice-%s.pdf' % self.legal_number
                file_content = data['data']['data']
                update_vals.update({
                    'vninvoice_representation_pdf': file_content,
                    'vninvoice_representation_filename_pdf': filename
                })
                message = _('Successfully downloaded the representation version of the VN-invoice %s.') % self.name

                # if the company wants attachment
                if self.company_id.sinvoice_representation_file_as_attachment or self._context.get('force_sinvoice_representation_file_as_attachment', False):
                    req_content = base64.decodebytes(file_content.encode())
                    attachment = (filename, req_content)
                    attachments.append(attachment)
                else:
                    message += _("\nYou will be able to find it in the tab E-Invoice of the invoice form view above.")

        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
            message = _("Something went wrong when get invoice file of the E-Invoice %s. Here is the debugging information:\n%s") % (self.legal_number, str(content))

        if update_vals:
            self.write(update_vals)
        if self._context.get('log_einvoice_message', False):
            self.message_post(body=message, attachments=attachments or None)
        return update_vals
    
    def _get_official_vninvoice(self):
        """
        this method allow to get data of E-invoice and then can convert it into PDF file
        :return:dictionary of return data
        {
        code: 0
        data: {"base64": "base64 string"
               "fileName": "string"   }
        message: "Thành công"
        succeeded: true of false
        }
        """
        self.ensure_one()
        self._check_download_invoice_after_issued()
        if not self.check_vninvoice_approved_and_signed:
            raise UserError(_("You cannot download the converted file of this invoice, because it's not signed"))
        update_vals = {}
        attachments = []
        try:
            if self.einvoice_api_version == 'v1':
                req = requests.post(
                    self.company_id.get_vninvoice_official_url(),
                    json=["%s" % (self.vninvoice_recordid)],
                    headers={"Content-type": "application/json",
                             "Authorization": "Bearer {}".format(self.company_id.get_vninvoice_api_token())}
                    )
            else:
                req = requests.post(
                    self.company_id.get_vninvoice_official_url().format(self.vninvoice_transactionid),
                    headers={"Content-type": "application/json",
                             "Authorization": "Bearer {}".format(self.company_id.get_vninvoice_api_token())}
                )
            req.raise_for_status()
            data = json.loads(req.text)
            if not data['succeeded']:
                message = _('Converted file of the invoice %s be downloaded unsuccessfully. Error: %s') % (self.name,data['message'])
            else:
                filename = 'VNinvoice-%s-converted.pdf' % self.legal_number
                file_content = data['data']['base64'] if self.einvoice_api_version == 'v1' else data['data']['data']
                update_vals.update({
                    'vninvoice_converted_file': file_content,
                    'vninvoice_converted_filename': filename
                })
                message = _('Successfully downloaded the converted version of the VN-invoice %s.') % self.name
                
                # if the company wants attachment
                if self.company_id.sinvoice_exchange_file_as_attachment or self._context.get('force_einvoice_converted_file_as_attachment', False):
                    req_content = base64.decodebytes(file_content.encode())
                    attachment = (filename, req_content)
                    attachments.append(attachment)
                else:
                    message += _("\nYou will be able to find it in the tab E-Invoice of the invoice form view above.")

        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
            message = _("Something went wrong when get invoice file of the E-Invoice %s. Here is the debugging information:\n%s") % (self.legal_number, str(content))

        if update_vals:
            self.write(update_vals)
        if self._context.get('log_einvoice_message', False):
            self.message_post(body=message, attachments=attachments or None)
        return update_vals
    
    def get_einvoice_converted_files(self):
        if (
            self.vninvoice_transactionid
            and (not self.vninvoice_converted_file
                 or self._context.get('refresh_vninvoice_converted_file', False)
                )
            ):
            self._get_official_vninvoice()
        return super(AccountMove, self).get_einvoice_converted_files()
    
    def _get_vninvoice_xml_data(self):
        """
        this method allow to get data of E-invoice and then can convert it into XML file
        :return: dictionary of return data
        {
        code: 0
        data: {"base64": "base64 string"
               "fileName": "string"   }
        message: "Thành công"
        succeeded: true of false
        }
        """
        self.ensure_one()
        self._check_download_invoice_after_issued()

        update_vals = {}
        attachments = []
        try:
            if self.einvoice_api_version == 'v1':
                req = requests.get(
                    self.company_id.get_vninvoice_download_xml_url().format(manoibo=self.company_id.get_vninvoice_company_code(), iderp=self.vninvoice_recordid),
                    headers={"Content-type": "application/json",
                             "Authorization": "Bearer {}".format(self.company_id.get_vninvoice_api_token())}
                    )
            else:
                req = requests.post(
                    self.company_id.get_vninvoice_download_xml_url().format(iderp=self.vninvoice_transactionid),
                    headers={"Content-type": "application/json",
                             "Authorization": "Bearer {}".format(self.company_id.get_vninvoice_api_token())},
                )
            req.raise_for_status()
            data = json.loads(req.text)
            if not data['succeeded']:
                message = _('XML files of the invoice %s be downloaded unsuccessfully. Error: %s') % (self.name,data['message'])
            else:
                filename = 'VNinvoice-%s.xml' % self.legal_number
                file_content = data['data']['base64'] if self.einvoice_api_version == 'v1' else data['data']['data']
                update_vals.update({
                    'vninvoice_representation_xml': file_content,
                    'vninvoice_representation_filename_xml': filename
                })
                message = _('Successfully downloaded the XML version of the VN-invoice %s.') % self.name
                
                # if the company wants attachment
                if self.company_id.sinvoice_representation_file_as_attachment or self._context.get('force_sinvoice_representation_file_as_attachment', False):
                    req_content = base64.decodebytes(file_content.encode())
                    attachment = (filename, req_content)
                    attachments.append(attachment)
                else:
                    message += _("\nYou will be able to find it in the tab E-Invoice of the invoice form view above.")
        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
            message = _("Something went wrong when get invoice file of the E-Invoice %s. Here is the debugging information:\n%s") % (self.legal_number, str(content))

        if update_vals:
            self.write(update_vals)
        if self._context.get('log_einvoice_message', False):
            self.message_post(body=message, attachments=attachments or None)
        return update_vals
    
    def get_einvoice_representation_files(self):
        # TODO: need to improve the code of this method and _ensure_vninvoice_representation_files method
        # to avoid checking the condition twice,
        # because both functions check the same condition
        if (
            self.vninvoice_transactionid
            and (
                not self.vninvoice_representation_pdf
                or self._context.get('refresh_vninvoice_representation_pdf', False)
                )
        ):
            self._get_unofficial_vninvoice()
        if (
            self.check_vninvoice_approved_and_signed
            and (
                not self.vninvoice_representation_xml
                or self._context.get('refresh_vninvoice_representation_xml', False)
                )
        ):
            self._get_unofficial_vninvoice()
            self._get_vninvoice_xml_data()
        return super(AccountMove, self).get_einvoice_representation_files()
    
    # TODO: need to improve in odoo 14
    def _ensure_vninvoice_representation_files(self, retries=0, sleep=3):
        """
        This method is to ensure converted file available

        :param retries: number of times to retry. vninvoice may not have these information right after issuing invoice
        :param sleep: number of second to wait before retrying

        :return: converted file in binary
        :rtype: bytes

        :raise MissingError: when no file available in VN-invoice system to get
        """
        self.ensure_one()
        if (
            not self.vninvoice_representation_pdf
            or (
                self.check_vninvoice_approved_and_signed
                and not self.vninvoice_representation_xml
                )
            or self._context.get('refresh_vninvoice_representation_pdf', False)
            or self._context.get('refresh_vninvoice_representation_xml', False)
        ):
            self.get_einvoice_representation_files()

        data = {
            'pdf': self.vninvoice_representation_pdf,
            'xml': self.vninvoice_representation_xml
            }
        if not data['pdf'] or (self.check_vninvoice_approved_and_signed and not data['xml']):
            if retries > 0:
                retries -= 1
                time.sleep(sleep)
                return self._ensure_vninvoice_representation_files(retries)
            else:
                raise MissingError(_("No representation files avaiable yet. Please wait for a few minutes before trying again!"))
        else:
            return data
    
    def _ensure_vninvoice_converted_file(self, retries=0, sleep=3):
        """
        This method is to ensure converted file available

        :param retries: number of times to retry. VN-Invoice may not have these information right after issuing invoice
        :param sleep: number of second to wait before retrying

        :return: converted file in binary
        :rtype: bytes
        
        :raise MissingError: when no file available in VN-Invoice system to get
        """
        self.ensure_one()
        if (self.check_vninvoice_approved_and_signed and not self.vninvoice_converted_file) or self._context.get('refresh_vninvoice_converted_file', False):
            self._get_official_vninvoice()

        if self.check_vninvoice_approved_and_signed and not self.vninvoice_converted_file:
            if retries > 0:
                retries -= 1
                time.sleep(sleep)
                return self._ensure_vninvoice_converted_file(retries)
            else:
                raise MissingError(_("No converted file avaiable yet. Please wait for a few minutes before trying again!"))
        else:
            return self.vninvoice_converted_file

    def cancel_vninvoice(self):
        for r in self:
            r._cancel_vninvoice()

    def _cancel_vninvoice(self,raise_error=True):
        self.ensure_one()
        if self.einvoice_state not in ['issued','paid']:
            raise UserError(_("The VN-invoice corresponding to the invoice %s could not be cancelled because"
                              " it has not been issued or cancelled already.")
                              % self.name)
        additional_ref_date = self._context.get('recordDate', fields.Datetime.now())
        # VN-invoice uses UTC+7
        additional_ref_date_utc7 = self.env['to.base'].convert_utc_time_to_tz(additional_ref_date, tz_name='Asia/Ho_Chi_Minh')
        req_data = {
            #Số biên bản
            'recordNo': self._context.get('recordNo'),
            #Lý do xóa hóa đơn
            'reason': self._context.get('reason'),
            # Tên văn bản thỏa thuận hủy hóa đơn
            'fileNameOfRecord': self._context.get('fileNameOfRecord'),
            # Ngày thỏa thuận huỷ hoá đơn, không vượt quá ngày hiện tại
            'recordDate': additional_ref_date_utc7.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            # File biên bản thu hổi
            'fileOfRecord': str(self._context.get('fileOfRecord'))
            }
        error = False
        # use new cursor to handle each invoice cancel
        # this could help commit a success cancel action before an error occurs that may roll back
        # the data in Odoo while the invoice is already cancel in VN-invoice database
        cr = registry(self._cr.dbname).cursor()
        self = self.with_env(self.env(cr=cr))
        params = {}
        try:
            if self.einvoice_api_version == 'v2':
                params.update({
                    'TemplateNo': self._get_vninvoice_template_name(),
                    'SerialNo': self._get_account_vninvoice_serial_name(),
                    'InvoiceNo': self.legal_number
                })
            if self.check_vninvoice_approved_and_signed:
                api_url = self.company_id.get_vninvoice_delete_url().format(self.vninvoice_transactionid)
            else:
                api_url = self.company_id.get_vninvoice_cancel_unsign_url().format(self.vninvoice_transactionid)
            if self.einvoice_api_version == 'v1' and not self.check_vninvoice_approved_and_signed:
                req = requests.delete(
                    api_url,
                    json=req_data,
                    headers={"Content-type": "application/json",
                             "Authorization": "Bearer {}".format(self.company_id.get_vninvoice_api_token())},
                    params=params
                    )
            else:
                req = requests.post(
                    api_url,
                    json=req_data,
                    headers={"Content-type": "application/json",
                             "Authorization": "Bearer {}".format(self.company_id.get_vninvoice_api_token())},
                    params=params
                    )
            req.raise_for_status()
            content = json.loads(req.text)
            if not content['succeeded']:
                error = True
                message = _("Could not cancel the E-invoice %s in VN-invoice system. Error: %s") % (self.legal_number or self.name, content['message'])
            else:
                message = _("The legal E-Invoice %s has been cancelled on VN-invoice.") % self.legal_number
                self.write({
                    'einvoice_state': 'cancelled',
                    'einvoice_cancellation_date': additional_ref_date,
                    })
                self.with_context(
                    refresh_vninvoice_representation_pdf=True,
                    refresh_vninvoice_representation_xml=True
                ).get_einvoice_representation_files()
                if self.check_vninvoice_approved_and_signed:
                    self.with_context(
                        refresh_vninvoice_converted_file=True
                    ).get_einvoice_converted_files()
        except requests.HTTPError as e:
            error = True
            message = _("Could not cancel the VN-invoice %s.") % self.legal_number
            if e.response.status_code == 500:
                message += _(" You might have not configured allowed IPs in your VN-invoice portal to grant access from your Odoo instance's IP."
                             " Or there could be something wrong with your VN-invoice's username and/or password.")
        if error and raise_error:
            cr.rollback()
            cr.close()
            raise ValidationError(message)
        self.message_post(body=message)
        cr.commit()
        cr.close()

    def _invoice_to_issue_einvoice(self):
        res = super(AccountMove, self)._invoice_to_issue_einvoice()
        return res.filtered(lambda move: move.invoice_date >= move.company_id.vninvoice_start_date if move.company_einvoice_provider == 'vninvoice' else True)

    def _get_report_base_filename(self):
        self.ensure_one()
        if self.journal_id.einvoice_send_mail_option == 'converted':
            name = self.vninvoice_converted_filename
        else:
            name = self.vninvoice_representation_filename_pdf
        if self.type in self.get_sale_types() and self.einvoice_state != 'not_issued' and name:
            name = '.'.join(name.split('.')[:-1])
            return ("%s") % name
        else:
            return super(AccountMove, self)._get_report_base_filename()
    
    @api.model
    def _prepare_invoice_info_values(self,data):
        dict = {}
        for index in range(0,len(data)):
            # with sign status = 5, invoice is signed
            dict[data[index]['idTransaction']] = (data[index]['signStatus'] == 5, data[index]['invoiceStatus'])
        return dict

    def _check_vninvoices_signed(self):
        context = self._context
        domain_account_move = [('einvoice_state', '!=', 'not_issued'),
                               ('vninvoice_transactionid', '!=', False),
                               ('check_vninvoice_approved_and_signed', '=', False),
                               ('type', 'in', self.get_sale_types()),
                               ('company_id', '=', context.get('company_vninvoice_id', self.env.company.id))]
        if 'active_ids' in context.keys():
            account_move_ids = context['active_ids']
            domain_account_move.append(('id','in',account_move_ids))
        account_moves = self.env['account.move'].search(domain_account_move)
        if account_moves:
            if self.einvoice_api_version == 'v1':
                einvoice_dates = account_moves.mapped('einvoice_invoice_date')
                # Convert datetime from UTC 0 to UTC +7 (VN-invoice system use UTC +7)
                fromdate = min(einvoice_dates) + relativedelta(hours=7)
                todate = max(einvoice_dates) + relativedelta(hours=7)
                r = account_moves[0]
                request_url = r.company_id.get_vninvoice_invoice_info_url().format(fromdate= fromdate.strftime('%Y/%m/%d'),
                                                                                   todate= todate.strftime('%Y/%m/%d'))
                try:
                    req = requests.get(request_url,
                        headers={"Content-type": "application/json",
                                 "Authorization": "Bearer {}".format(r.company_id.get_vninvoice_api_token())}
                        )
                    req.raise_for_status()
                    data = json.loads(req.text)
                    invoices_info = self._prepare_invoice_info_values(data)
                    for record in account_moves:
                        if invoices_info.get(record.vninvoice_transactionid, False):
                            record.check_vninvoice_approved_and_signed = invoices_info[record.vninvoice_transactionid][0]
                except:
                    pass
            else:
                for r in account_moves:
                    request_url = r.company_id.get_vninvoice_invoice_info_url()
                    try:
                        req = requests.get(request_url,
                                           headers={
                                               "Content-type": "application/json",
                                               "Authorization": "Bearer {}".format(r.company_id.get_vninvoice_api_token())
                                           },
                                           params={
                                               'TemplateNo': r._get_vninvoice_template_name(),
                                               'SerialNo': r._get_account_vninvoice_serial_name(),
                                               'InvoiceNo': r.legal_number
                                           })
                        req.raise_for_status()
                        data = json.loads(req.text)
                        r.check_vninvoice_approved_and_signed = data['signStatus'] == 5
                    except requests.HTTPError as e:
                        content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
                        r.message_post(body=_("Something went wrong when checking Sign status of E-Invoice %s. Here is the debugging information:\n%s") % (self.legal_number, str(content)))


    def _action_check_vninvoices_signed(self):
        companies = self.env['account.move'].browse(self._context['active_ids']).mapped('company_id')
        for r in companies:
            self.with_context(company_vninvoice_id=r.id)._check_vninvoices_signed()

    def _action_notif_einvoice_error(self):
        self.ensure_one()
        data = {
            'erpId': self.vninvoice_transactionid,
            'reason': self._context.get('reason'),
            'action': int(self._context.get('action')),
        }
        try:
            req = requests.post(
                self.company_id.get_vninvoice_invoice_error_notification(),
                json=data,
                headers={"Content-type": "application/json",
                         "Authorization": "Bearer {}".format(self.company_id.get_vninvoice_api_token())},
            )
            req.raise_for_status()
            self.einvoice_error_notif_state = 'draft'
            self.message_post(body=_("Creating e-invoice error notification is successful"))
        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
            raise UserError(_("Something went wrong when Creating E-Invoice Error Notification. Here is the debugging information:\n%s") % str(content['error']['message']))

    def action_sign_einvoice_error_notif(self):
        for r in self:
            r._action_sign_einvoice_error_notif()

    def _action_sign_einvoice_error_notif(self):
        self.ensure_one()
        try:
            req = requests.post(
                self.company_id.get_vninvoice_invoice_sign_error_notification(),
                json=[self.vninvoice_transactionid],
                headers={"Content-type": "application/json",
                         "Authorization": "Bearer {}".format(self.company_id.get_vninvoice_api_token())},
            )
            req.raise_for_status()
            self.einvoice_error_notif_state = 'signed'
            self.message_post(body=_("Sign e-invoice error notification is successful"))
        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
            raise UserError(_("Something went wrong when signing E-Invoice Error Notification. Here is the debugging information:\n%s") % str(content))

    def action_delete_einvoice_error_notif(self):
        for r in self:
            r._action_delete_einvoice_error_notif()

    def _action_delete_einvoice_error_notif(self):
        self.ensure_one()
        try:
            req = requests.post(
                self.company_id.get_vninvoice_invoice_delete_error_notification(),
                json={'erpId': self.vninvoice_transactionid},
                headers={"Content-type": "application/json",
                         "Authorization": "Bearer {}".format(self.company_id.get_vninvoice_api_token())},
            )
            req.raise_for_status()
            self.einvoice_error_notif_state = 'none'
            self.message_post(body=_("Deleting e-invoice error notification is successful"))
        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
            raise UserError(_("Something went wrong when deleting E-Invoice Error Notification. Here is the debugging information:\n%s") % str(content))
   
    def action_sync_vninvoice_status(self):
        v1_moves = self.filtered(lambda inv: inv.einvoice_api_version == 'v1' 
                                and inv.einvoice_state in ('issued', 'paid', 'adjusted')
                                and inv.vninvoice_transactionid
                                and inv.access_token)
        v2_moves = self.filtered(lambda inv: inv.einvoice_api_version == 'v2' 
                                and inv.einvoice_state in ('issued', 'paid', 'adjusted')
                                and inv.vninvoice_transactionid
                                and inv.access_token)
        if v1_moves:
            einvoice_dates = v1_moves.mapped('einvoice_invoice_date')
            # Convert datetime from UTC 0 to UTC +7 (VN-invoice system use UTC +7)
            from_date = min(einvoice_dates) + relativedelta(hours=7)
            to_date = max(einvoice_dates) + relativedelta(hours=7)
            move = v1_moves[0]
            api_url = move.company_id.get_vninvoice_invoice_info_url().format(fromdate= from_date.strftime('%Y/%m/%d'),
                                                                       todate= to_date.strftime('%Y/%m/%d'))
            try:
                req = requests.get(api_url,
                    headers={"Content-type": "application/json",
                             "Authorization": "Bearer {}".format(move.company_id.get_vninvoice_api_token())}
                    )
                req.raise_for_status()
                data = json.loads(req.text)
                invoices_info = self._prepare_invoice_info_values(data)
                for move in v1_moves:
                    if invoices_info.get(move.vninvoice_transactionid, False):
                        if invoices_info[move.vninvoice_transactionid][1] in (2, 9):
                            move.write({'einvoice_state': 'cancelled'})
                            if move.check_vninvoice_approved_and_signed:
                                move.with_context(
                                    refresh_sinvoice_representation_file=True,
                                    refresh_vninvoice_representation_xml=True
                                ).get_einvoice_representation_files()
                                move.with_context(
                                    refresh_vninvoice_converted_file=True
                                ).get_einvoice_converted_files()
            except requests.HTTPError as e:
                content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
                raise UserError(_("Something went wrong when synchronizing E-Invoice status. Here is the debugging information:\n%s") % str(content))
        for m in v2_moves:
            api_url = m.company_id.get_vninvoice_invoice_info_url()
            try:
                req = requests.get(api_url,
                                   headers={
                                       "Content-type": "application/json",
                                       "Authorization": "Bearer {}".format(m.company_id.get_vninvoice_api_token())
                                   },
                                   params={
                                       'TemplateNo': m._get_vninvoice_template_name(),
                                       'SerialNo': m._get_account_vninvoice_serial_name(),
                                       'InvoiceNo': m.legal_number
                                   })
                req.raise_for_status()
                data = json.loads(req.text)
                if data.get('invoiceStatus', -1) in (2, 9):
                    m.write({'einvoice_state': 'cancelled'})
                    if m.check_vninvoice_approved_and_signed:
                        m.with_context(
                            refresh_vninvoice_representation_pdf=True,
                            refresh_vninvoice_representation_xml=True
                        ).get_einvoice_representation_files()
                        m.with_context(
                            refresh_vninvoice_converted_file=True
                        ).get_einvoice_converted_files()
            except requests.HTTPError as e:
                content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
                m.message_post(body=_("Something went wrong when synchronizing status for E-Invoice %s. Here is the debugging information:\n%s") % (self.legal_number, str(content)))

    @api.model
    def _cron_ensure_einvoice_download_file(self):
        invoices = self.env['account.move'].search([('einvoice_state', '!=', 'not_issued'),('vninvoice_transactionid', '!=', False)])
        for invoice in invoices:
            try:
                invoice._ensure_vninvoice_representation_files()
                invoice._ensure_vninvoice_converted_file()
            except:
                continue
        return super(AccountMove, self)._cron_ensure_einvoice_download_file()

    def _cron_check_vninvoices_signed(self):
        companies = self.env['res.company'].search([('einvoice_provider','!=', 'none')])
        if companies:
            for r in companies:
                self.with_context(company_vninvoice_id=r.id)._check_vninvoices_signed()
