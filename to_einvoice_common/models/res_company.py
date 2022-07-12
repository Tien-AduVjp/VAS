from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    einvoice_provider = fields.Selection([('none','None')], copy=False, required=True, default='none', string='E-Invoice Provider')
    einvoice_lock_legal_number = fields.Boolean(string='Lock Legal Number', default=True,
                                              help="If checked, invoice's legal number will be locked after E-Invoice will be issued.")
    einvoice_issue_earliest_invoice_first = fields.Boolean(string='Issue Earlier Invoice First', default=True,
                                                         help="If checked, during issuing a new E-Invoice, Odoo will check to validate if there is an"
                                                         " existing invoice the invoice date of which is earlier than the current one's. If there is,"
                                                         " Odoo will stop you from issuing E-Invoice for the current one and ask you to do for the"
                                                         " earlier one priorily.")
    # TODO: need to rename fields in version 14.0
    sinvoice_exchange_file_as_attachment = fields.Boolean(string='Attach Invoice Converted Version', default=False,
                                                          help="If checked, when generating the converted version of the E-Invoice,"
                                                          " Odoo will also generate a corresponding attachment and attach it to the invoice.")
    sinvoice_representation_file_as_attachment = fields.Boolean(string='Attach Invoice Repensentation Version', default=False,
                                                                help="If checked, when generating the representation version of the E-Invoice,"
                                                                " Odoo will also generate a corresponding attachment and attach it to the invoice.")
    einvoice_auto_issue = fields.Boolean(string='Auto Issue', copy=False, help="If checked, the system automatically issue e-invoices.")
    einvoice_api_version = fields.Selection([('v1', 'V1'), ('v2', 'V2')], string='API Version', default='v1',
                                            copy=False, required=True,
                                            help="Versions corresponding to laws of rule in Viet Nam:"
                                                 "\nV1 for TT32"
                                                 "\nV2 for TT78"
                                                 "\nYou should check the version of your e-invoice webservices before choosing versions here")
