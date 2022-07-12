from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    account_sinvoice_serial_id = fields.Many2one('account.sinvoice.serial', string='S-Invoice Serial',
                                                 help="The prefix (e.g. AA/16E, AA/17E, etc) of the invoice number that must be registered with"
                                                 " S-Invoice priorily. See the Circular No. 39/2014/TT-BTC dated March 31, 2014 by The Ministry"
                                                 " of Finance of Vietnam.\n"
                                                 "Note: If this is not set, Odoo will use the one specified in the global Settings")
    account_sinvoice_template_id = fields.Many2one('account.sinvoice.template', string='S-Invoice Template', compute='_compute_account_sinvoice_template_id', store=True, readonly=False,
                                                   help="The template that you have registered with S-Invoice for redering your invoices of this template.\n"
                                                   "Note: If this is not set, Odoo will use the one specified in the global Settings")
    account_sinvoice_type_id = fields.Many2one('account.sinvoice.type', string='S-Invoice Type', compute='_compute_account_sinvoice_type_id', store=True, readonly=False,
                                               help="The invoice type provided by Viettel S-Invoice. Leave it empty to use the one specified in the global Settings.\n"
                                               "Note: If this is not set, Odoo will use the one specified in the global Settings")

    def get_sinvoice_template(self):
        return self.account_sinvoice_template_id or self.company_id.account_sinvoice_template_id

    def get_account_sinvoice_type(self):
        return self.account_sinvoice_type_id or self.company_id.account_sinvoice_type_id

    def get_account_sinvoice_serial(self):
        return self.account_sinvoice_serial_id or self.company_id.account_sinvoice_serial_id

    @api.depends('account_sinvoice_serial_id')
    def _compute_account_sinvoice_template_id(self):
        for r in self:
            r.account_sinvoice_template_id = False
            if r.account_sinvoice_serial_id:
                if r.account_sinvoice_serial_id.template_id:
                    r.account_sinvoice_template_id = r.account_sinvoice_serial_id.template_id

    @api.depends('account_sinvoice_template_id')
    def _compute_account_sinvoice_type_id(self):
        for r in self:
            r.account_sinvoice_type_id = False
            if r.account_sinvoice_template_id:
                if r.account_sinvoice_template_id.type_id:
                    r.account_sinvoice_type_id = r.account_sinvoice_template_id.type_id
