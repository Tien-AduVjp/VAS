from odoo import models, fields, api, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    company_einvoice_provider = fields.Selection(string='Company E-Invoice Provider', related='company_id.einvoice_provider', help="Technical field to indicate E-Invoice provider of company")
    einvoice_disabled = fields.Boolean(string='E-Invoice Disabled',
                                      help="If checked, E-Invoice integration will be disabled for all the invoices"
                                      " of this journal no matter it is enabled at company level or not.")
    einvoice_enabled = fields.Boolean(string='E-Invoice Enabled', compute='_compute_einvoice_enabled', store=True,
                                      help="Technical field to indicate if E-Invoice is enabled for invoices of this journal")
    einvoice_item_name = fields.Selection([
        ('invoice_line_name', 'Invoice Line Description'),
        ('invoice_line_product', 'Product Name')],
        default='invoice_line_name', string='E-Invoice Item', required=True, help="This option allows you to choose between product name and invoice line description"
        " for issuing E-Invoice:\n"
        "- Invoice Line Description: the description of Odoo's invoice lines will be sent to E-Invoice system for items name;\n"
        "- Product Name: the name of Odoo's invoice line product will be sent to E-Invoice system for items name;\n")
    send_mail_einvoice_disabled = fields.Boolean(string='Disable Send E-Invoice PDF by email',
                                               help="By default, Odoo will replace it's standard invoice PDF with E-Invoice PDF"
                                               " when E-Invoice is enabled for the invoice. By checking this, you will be able to disable"
                                               " such behaviour for invoices of this journal to fallback to the standard behaviour")
    einvoice_item_name_new_line_replacement = fields.Char(string='E-invoice item name new line replacement ', default='; ', trim=False, help="The character(s) with "
                                                          "which the new line character(s) in the E-Invoice item name will be replaced.")    
    einvoice_item_name_limit = fields.Integer(string='E-invoice item name limit', required=True, default=300, help="Maximum number of characters for E-Invoice item name.")
    einvoice_send_mail_option = fields.Selection([
        ('display', 'Display Version'),
        ('converted', 'Converted Version')
        ],
        default='display', required=True, string='E-Invoice Send Mail/Portal option', help="Choose which version of E-Invoice will be available"
        " for mail sending and download and print from customer portal.")
    einvoice_display_bank_account = fields.Boolean(help=_("If checked, this bank account information will be displayed on E-Invoice"),
                                        domain="[('type','=','bank)]", string="E-invoice Bank Info.")
    einvoice_auto_issue = fields.Boolean(string='Auto Issue', copy=False, default=lambda self: self.company_id.einvoice_auto_issue,
                                         help="If checked, the system automatically issue e-invoices.")

    @api.depends('einvoice_disabled', 'company_id.einvoice_provider','type')
    def _compute_einvoice_enabled(self):
        for r in self:
            r.einvoice_enabled = not r.einvoice_disabled and r.company_id.einvoice_provider != 'none' and r.type == 'sale'
