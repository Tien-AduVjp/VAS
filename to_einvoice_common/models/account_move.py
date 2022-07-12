import logging
import datetime

from odoo import models,fields,api,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_date

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'to.vietnamese.number2words']

    company_einvoice_provider = fields.Selection(related='journal_id.company_einvoice_provider', help="Technical field to indicate E-Invoice provider of company")
    einvoice_enabled = fields.Boolean(related='journal_id.einvoice_enabled',
                                      help="This technical field is to indicate if E-Invoice service is available for this invoice")
    einvoice_auto_issue = fields.Boolean(related='journal_id.einvoice_auto_issue')
    einvoice_state = fields.Selection([
        ('not_issued', 'Not Issued'),
        ('issued', 'Issued and not Paid'),
        ('paid', 'Paid'),
        ('adjusted', 'Adjusted'),
        ('cancelled', 'Issued but Cancelled')
        ], string='E-Invoice Status', copy=False, index=True, required=True, default='not_issued', readonly=True, tracking=True)
    einvoice_invoice_date = fields.Datetime(string='E-Invoice Issued Date', copy=False, readonly=True, tracking=True,
                                        help="The date and time at which the E-Invoice was issued.")
    einvoice_cancellation_date = fields.Datetime(string='E-Invoice Cancellation Date', copy=False, readonly=True, tracking=True,
                                        help="The cancellation date of the E-Invoice which may differ from the date on which the cancel request was sent to E-Invoice.")
    einvoice_issue_user_id = fields.Many2one('res.users', string='E-Invoice Issue User', copy=False, readonly=True, tracking=True,
                                             help="The user who issued the E-Invoice for this invoice")
    lock_legal_number = fields.Boolean(string='Lock Legal Number', compute='_compute_lock_legal_number',
                                              help="If checked, invoice's legal number will be locked after E-Invoice will be issued.")
    total_in_word = fields.Char(string='In words', compute='_compute_num2words')

    cancellation_record = fields.Binary(string='The minutes of invoice withdrawal (PDF)',
                                      help="The file of the agreement between you and your customer for the invoice cancellation.")
    cancellation_record_name = fields.Char(string='File Name')
    adjustment_record = fields.Binary(string='Adjustment File Agreement (PDF)',
                                      help="The file of the agreement between you and your customer for adjustment invoice.")
    adjustment_record_name = fields.Char(string='Adjustment File Name')
    reversed_entry_einvoice_state = fields.Selection(related='reversed_entry_id.einvoice_state', string='Reversed E-invoice State')
    einvoice_api_version = fields.Selection(related='company_id.einvoice_api_version')
    einvoice_error_notif_state = fields.Selection(selection=[
        ('none', 'None'),
        ('draft', 'Draft'),
        ('signed', 'Signed'),
    ], default='none', copy=False, readonly=True)

    @api.constrains('cancellation_record_name')
    def _check_cancellation_record(self):
        for r in self:
            if r.cancellation_record_name:
                if r.cancellation_record_name[-4:] != '.pdf':
                    raise ValidationError(_("The minutes of invoice withdrawal  must be PDF file."))
                
    @api.constrains('state')
    def _check_state(self):
        for r in self:
            if r.einvoice_state and r.einvoice_state not in ('not_issued', 'cancelled'):
                raise ValidationError(_("You cannot change state of the invoice '%s' while it was issuing." 
                                        "You can cancel the einvoice in provider 's system first, then try again later.") % (r.name or r.legal_number,))
            
    def _compute_num2words(self):
        for r in self:
            r.total_in_word = r.num2words(r.amount_total, precision_rounding=r.currency_id.rounding)
            
    def _compute_lock_legal_number(self):
        for r in self:
            if r.einvoice_enabled and r.company_id.einvoice_lock_legal_number and r.einvoice_state != 'not_issued':
                r.lock_legal_number = True
            else:
                r.lock_legal_number = False

    def _get_cusomter_invoice_address(self):
        return self.partner_id if self.partner_id.type == 'invoice' else self.commercial_partner_id

    def _get_issuing_user(self):
        return self.user_id or self.env.user

    # Name of seller in e invoice
    def _prepare_einvoice_seller_legal_name(self):
        ctx = dict(self._context).copy()
        ctx['lang'] = self.env.ref('base.lang_vi_VN').code
        name = self.with_context(ctx).company_id.partner_id.name
        ctx['lang'] = self.env.ref('base.lang_en').code
        en_name = self.with_context(ctx).company_id.partner_id.name
        if en_name != name and self._einvoice_need_english():
            name += " (%s)" % en_name
        return name

    def _prepare_update_vals_after_issuing(self, returned_vals):
        """
        This method is called by the method `_issue_einvoice`. This prepares data to write back to the current invoice after issuing on E-Invoice system

        @param returned_vals: the result that returned by E-Invoice system after issuing the invoice
        @return: dictionary of values to update the current invoice after issuing
        @rtype: dict
        """
        if self.type == 'out_refund':
            self.reversed_entry_id.write({'einvoice_state': 'adjusted'})
        return {
            'einvoice_invoice_date': fields.Datetime.now(),
            'einvoice_state': 'paid' if self.invoice_payment_state == 'paid' else 'issued',
            'einvoice_issue_user_id': self.env.user.id,
            }

    def _einvoice_need_english(self):
        """
        This method is to check if this invoice does need subtitle in English during issuing E-Invoice
        """
        if self.commercial_partner_id.country_id and self.commercial_partner_id.country_id != self.env.ref('base.vn'):
            return True
        else:
            return False
    
    def _prepare_invoice_tax_data(self):
        '''
        Method to prepare tax data of invoices according to each tax
        '''
        invoice_tax = []
        for line in self.invoice_line_ids.filtered(lambda line: not line.display_type):
            # E-Invoice does not accept negative Untaxed Subtotal
            price_subtotal = abs(line.price_subtotal)
            # E-Invoice does not accept negative Taxed Subtotal
            price_total = abs(line.price_total)

            # Create tax data
            tax = line.tax_ids
            # TODO: add configuration switch to do on/off multiple taxes on a single invoice line check
            if len(tax) > 1:
                raise ValidationError(
                    _("Multiple taxes on a single invoice line is not supported by einvoice provider %s") % line.move_id.company_einvoice_provider)
            count = 0
            if invoice_tax:
                for tax_line in invoice_tax:
                    if tax.id == tax_line['id'] or (tax.amount == tax_line['percent'] and tax.tax_group_id.id == tax_line['tax_group_id']):
                        count = 1
                        # We need to round because 27.72 + 417.69 = 445.40999999999997
                        # so, an error occured on einvoice system
                        tax_line['amount'] = self.currency_id.round(tax_line['amount'] + price_subtotal)
                        tax_line['amount_tax'] = self.currency_id.round(tax_line['amount_tax'] + price_total - price_subtotal)
                        break
            if count == 0:
                invoice_tax.append({
                    'id': tax.id,
                    'name': tax.with_context(lang=self.env.ref('base.lang_vi_VN').code).tax_group_id.name,
                    'tax_group_id':tax.tax_group_id.id,
                    'percent': tax.amount,
                    'amount_type': tax.amount_type,
                    'amount': price_subtotal,
                    'amount_tax': self.currency_id.round(price_total - price_subtotal),
                })
        return invoice_tax

    def _check_general_infor(self):
        self.ensure_one()

        # check invoice
        if self.type not in self.get_sale_types():
            raise UserError(_("Only customer invoices can generate E-Invoice!"))
        if self.state != 'posted' or self.invoice_payment_state not in ('not_paid','paid'):
            raise ValidationError(_("You cannot generate E-Invoice from the Odoo invoice %s while the Odoo invoice status is neither Open nor Paid")
                                  % (self.name or self.legal_number,))
        if self.einvoice_state != 'not_issued':
            raise UserError(_("E-Invoice for the invoice %s has been issued already!") % (self.name or self.legal_number,))
        if self.type == 'out_refund' and self.reversed_entry_id.currency_id != self.currency_id:
            raise UserError(_("You cannot issue this adjustment invoice because of the currency difference between original invoice %s and it") % self.reversed_entry_id.display_name)

        # check customer
        customer = self._get_cusomter_invoice_address()
        if not customer.street:
            raise ValidationError(_("Please specify address for the customer %s.") % customer.name)
        if not customer.country_id:
            raise ValidationError(_("Please specify a country for the customer %s.") % customer.name)
        # VAT number is required for enterprise customers in Vietnam
        if customer.country_id == self.env.ref('base.vn') and self.commercial_partner_id.is_company and not self.commercial_partner_id.vat:
            raise ValidationError(_("You must provide Tax Identication Number of the customer %s.") % self.commercial_partner_id.name)
        
        # Check company
        if not self.company_id.street:
            raise ValidationError(_("Please specify your company address before you can issue an E-Invoice"))
        if not self.company_id.vat:
            raise ValidationError(_("You have not configured Tax Identication Number for your company %s.") % self.company_id.name)
        
    def _check_invoice_date(self, einvoice_start_date):
        if self.invoice_date != fields.Date.today():
            raise UserError(_("You may not be able issue e-invoices for the invoice '%s' with invoice date different from the current date."
                              "This is inconsistent with the current provisions of the law.") % (self.name or self.legal_number,))

        if einvoice_start_date and self.invoice_date and self.invoice_date < einvoice_start_date:
            raise UserError(_("You cannot issue E-Invoice for the invoices %s that has invoice date earlier than the company's"
                              " E-Invoice Start Date (%s). If you still want to do it, you could either:\n"
                              "* Change the date of the invoice to a date that is later than or equal to %s;\n"
                              "* Or, go to Accounting > Configuration > Settings and change E-Invoice Start Date to"
                              " a date that is earlier than or equal to %s.")
                              % (
                                  self.name,
                                  format_date(self.env, einvoice_start_date),
                                  format_date(self.env, einvoice_start_date),
                                  format_date(self.env, self.invoice_date)
                                  )
                              )

        if self.company_id.einvoice_issue_earliest_invoice_first and einvoice_start_date:
            earlier_invoice = self._find_earliest_unissued_customer_invoice(einvoice_start_date)
            if earlier_invoice:
                raise UserError(_("You should issue E-Invoice for the invoice %s dated %s before issuing E-Invoice for the current one %s dated %s."
                                  " Or, you could go to Accounting > Configuration > Settings to disable this verification although you are not"
                                  " recommended to do that unless you know what you do.")
                                % (
                                    earlier_invoice.name or earlier_invoice.legal_number,
                                    format_date(self.env, earlier_invoice.invoice_date),
                                    self.name or self.legal_number,
                                    format_date(self.env, self.invoice_date)
                                    ),
                                )
    def _check_download_invoice_after_issued(self):
        if self.einvoice_state == 'not_issued':
            raise UserError(_("The E-invoice corresponding to the invoice %s could not be downloaded because"
                              " it has not been issued.")
                              % self._name)
        if self.type not in self.get_sale_types():
            raise UserError(_("Could not download E-invoice as the invoice %s is not a customer invoice")
                            % (self.name or self.legal_number,))
        if not self.legal_number:
            raise UserError(_("The invoice %s has no legal number. This could be a data inconsitant problem. Please contact your service provider for help")
                            % self.legal_number)
    
    def _find_earliest_unissued_customer_invoice(self,einvoice_start_date):
        """
        This method finds the earliest unissued customer invoice / credit note
        """
        self.ensure_one()
        domain = [
            ('state', '!=', 'cancel'),
            ('type', '=', 'out_invoice'),
            ('einvoice_state', '=', 'not_issued'),
            ('invoice_date', '<', self.invoice_date),
            ('journal_id.einvoice_enabled', '=', True)
        ]
        if einvoice_start_date:
            domain.append(('invoice_date', '>', einvoice_start_date))
        return self.env['account.move'].search(domain, order='invoice_date asc, id asc', limit=1)

    def _phone_format(self,phone_number):
        # Remove blank, minus and plus in customer phone number
        phone_number = phone_number.replace(' ', '').replace('-', '').replace('+', '00').replace('(', '').replace(')','')
        return phone_number
    
    def action_sync_einvoice_status(self):
        providers = self.mapped('company_einvoice_provider')
        for provider in set(providers):
            moves = self.filtered(lambda m: m.company_einvoice_provider == provider)
            method = 'action_sync_%s_status' % provider
            if moves and hasattr(moves, method):
                getattr(moves, method)()
    
    def _issue_einvoice(self,raise_error):
        ''' 
        Hook method for potential inheritance
        '''
        pass

    def issue_einvoices(self, raise_error=True):
        # we sort the invoices to ensure the earliest invoice should be at the first position
        # otherwise, we will get error during invoice generation
        self = self.sorted('invoice_date')
        error_invoices = self.env['account.move']
        for r in self:
            if r._einvoice_need_english():
                lang = self.env.ref('base.lang_en').code
            else:
                lang = self.env.ref('base.lang_vi_VN').code
            res = r.with_context(lang=lang)._issue_einvoice(raise_error)
            if res:
                error_invoices |= r
        return error_invoices, self - error_invoices


    def action_issue_einvoices(self):
        if self.einvoice_state == 'not_issued':
            self.issue_einvoices(raise_error=True)
    
    def get_einvoice_representation_files(self):
        pass
    
    def get_einvoice_converted_files(self):
        pass

    def _invoice_to_issue_einvoice(self):
        '''
        Hook method for potential inheritance
        '''
        return self.env['account.move'].search([
            ('state', '=', 'posted'),
            ('invoice_payment_state', 'in', ('not_paid', 'paid')),
            ('einvoice_state', '=', 'not_issued'),
            ('einvoice_enabled', '=', True),
            ('einvoice_auto_issue', '=', True)
        ])

    @api.model
    def cron_issue_einvoices(self):
        # TODO: remove me in master/14+
        self._cron_issue_einvoices()

    @api.model
    def _cron_issue_einvoices(self):
        invoices = self._invoice_to_issue_einvoice()
        for invoice in invoices:
            try:
                with invoice.env.cr.savepoint():
                    invoice.issue_einvoices(raise_error=False)
            except Exception as e:
                _logger.error("Could not issue E-Invoice for the invoice %s. Here is the debugging information: %s" % (invoice.name, str(e)))
                continue
        
    @api.model
    def _cron_ensure_einvoice_download_file(self):
        #this method is inherited by modules of e-invoice providers to use shared cron.  
        pass

