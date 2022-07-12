from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    einvoice_disabled = fields.Boolean(string='E-Invoice Disabled',
                                      help="If checked, E-Invoice integration will be disabled for all the invoices"
                                      " of this journal no matter it is enabled at company level or not.")
    einvoice_enabled = fields.Boolean(string='E-Invoice Enabled', compute='_compute_einvoice_enabled', store=True,
                                      help="Technical field to indicate if E-Invoice is enabled for invoices of this journal")
    einvoice_item_name = fields.Selection([
        ('invoice_line_name', 'Invoice Line Description'),
        ('invoice_line_product', 'Product Name')],
        default='invoice_line_name', string='E-Invoice Item', help="This option allows you to choose between product name and invoice line description"
        " for issuing E-Invoice:\n"
        "- Invoice Line Description: the description of Odoo's invoice lines will be sent to E-Invoice system for items name;\n"
        "- Product Name: the name of Odoo's invoice line product will be sent to E-Invoice system for items name;\n")
    send_mail_einvoice_disabled = fields.Boolean(string='Disable Send E-Invoice PDF by email',
                                               help="By default, Odoo will replace it's standard invoice PDF with E-Invoice PDF"
                                               " when E-Invoice is enabled for the invoice. By checking this, you will be able to disable"
                                               " such behaviour for invoices of this journal to fallback to the standard behaviour")
    einvoice_item_name_new_line_replacement = fields.Char(string='E-invoice item name new line replacement ', default='; ', trim=False, help="The character(s) with "
                                                          "which the new line character(s) in the E-Invoice item name will be replaced.")
    einvoice_item_name_limit = fields.Integer(string='E-invoice item name limit', default=300, help="Maximum number of characters for E-Invoice item name.")
    einvoice_send_mail_option = fields.Selection([
        ('display', 'Display Version'),
        ('converted', 'Converted Version')
        ],
        default='display', string='E-Invoice Send Mail/Portal option', help="Choose which version of E-Invoice will be available"
        " for mail sending and download and print from customer portal.")
    einvoice_display_bank_account = fields.Boolean(help=_("If checked, this bank account information will be displayed on E-Invoice"),
                                                   string="E-invoice Bank Info.")
    einvoice_service_id = fields.Many2one(related='company_id.einvoice_service_id')
    account_einvoice_serial_id = fields.Many2one('account.einvoice.serial', string='E-Invoice Serial',
                                                 domain="[('einvoice_service_id', '=', einvoice_service_id), ('deprecated', '=', False)]",
                                                 help="The prefix (e.g. AA/16E, AA/17E, etc) of the invoice number that must be registered with"
                                                      " E-Invoice priorily. See the Circular No. 39/2014/TT-BTC dated March 31, 2014 by The Ministry"
                                                      " of Finance of Vietnam.\n"
                                                      "Note: If this is not set, Odoo will use the one specified in the global Settings")
    account_einvoice_template_id = fields.Many2one('account.einvoice.template', string='E-Invoice Template',
                                                   compute='_compute_account_einvoice_template_id', store=True, readonly=False,
                                                   help="The template that you have registered with E-Invoice provider for rendering your invoices of this template.\n"
                                                   "Note: If this is not set, Odoo will use the one specified in the global Settings")
    account_einvoice_type_id = fields.Many2one('account.einvoice.type', string='E-Invoice Type',
                                               compute='_compute_account_einvoice_type_id', store=True, readonly=False,
                                               help="The invoice type provided by E-Invoice provider. Leave it empty to use the one specified in the global Settings.\n"
                                               "Note: If this is not set, Odoo will use the one specified in the global Settings")
    einvoice_auto_issue = fields.Boolean(string='Auto Issue', copy=False,
                                         default=lambda self: self.company_id.einvoice_auto_issue,
                                         help="If checked, the system automatically issue e-invoices.")

    @api.constrains('type', 'einvoice_item_name', 'einvoice_item_name_limit', 'einvoice_send_mail_option')
    def _check_required_fields(self):
        for r in self:
            if r.type == 'sale':
                if r.einvoice_enabled and not r.einvoice_item_name:
                    raise ValidationError(_("E-Invoice Item must be required for journal %s."
                                            " Please input E-Invoice Item for journal %s."
                                            " or Disable E-Invoice")
                                            % (r.name, r.name))
                if  r.einvoice_enabled and not r.einvoice_item_name_limit:
                    raise ValidationError(_("E-invoice item name limit must be required for journal %s."
                                            " Please input E-invoice item name limit for journal %s."
                                            " or Disable Send E-Invoice PDF by email")
                                            % (r.name, r.name))
                if not r.send_mail_einvoice_disabled and not r.einvoice_send_mail_option:
                    raise ValidationError(_("E-Invoice Send Mail/Portal option must be required for journal %s."
                                            " Please input E-Invoice Send Mail/Portal option for journal %s."
                                            " or Disable E-Invoice")
                                            % (r.name, r.name))

    @api.depends('einvoice_disabled', 'type')
    def _compute_einvoice_enabled(self):
        for r in self:
            r.einvoice_enabled = not r.einvoice_disabled and r.type == 'sale'

    @api.depends('account_einvoice_serial_id')
    def _compute_account_einvoice_template_id(self):
        for r in self:
            r.account_einvoice_template_id = r.account_einvoice_serial_id.template_id

    @api.depends('account_einvoice_template_id')
    def _compute_account_einvoice_type_id(self):
        for r in self:
            r.account_einvoice_type_id = r.account_einvoice_template_id.type_id

    def get_account_einvoice_serial(self):
        return self.account_einvoice_serial_id

    def get_einvoice_template(self):
        return self.account_einvoice_template_id or self.account_einvoice_serial_id.template_id

    def get_account_einvoice_type(self):
        return self.account_einvoice_type_id or self.account_einvoice_serial_id.type_id
