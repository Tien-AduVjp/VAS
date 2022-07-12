from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    account_vninvoice_serial_id = fields.Many2one('account.vninvoice.serial', string='VN-invoice Serial',
                                                 help="The prefix (e.g. AA/16E, AA/17E, etc) of the invoice number that must be registered with"
                                                 " VN-invoice priorily. See the Circular No. 39/2014/TT-BTC dated March 31, 2014 by The Ministry"
                                                 " of Finance of Vietnam.\n"
                                                 "Note: If this is not set, Odoo will use the one specified in the global Settings")
    account_vninvoice_template_id = fields.Many2one('account.vninvoice.template', string='VN-invoice Template', compute='_compute_account_vninvoice_template_id', store=True, readonly=False,
                                                   help="The template that you have registered with VN-invoice for rendering your invoices of this template.\n"
                                                   "Note: If this is not set, Odoo will use the one specified in the global Settings")
    account_vninvoice_type_id = fields.Many2one('account.vninvoice.type', string='VN-invoice Type', compute='_compute_account_vninvoice_type_id', store=True, readonly=False,
                                               help="The invoice type provided by VN-invoice. Leave it empty to use the one specified in the global Settings.\n"
                                               "Note: If this is not set, Odoo will use the one specified in the global Settings")

    def get_vninvoice_template(self):
        return self.account_vninvoice_template_id or self.company_id.account_vninvoice_template_id

    def get_account_vninvoice_serial(self):
        return self.account_vninvoice_serial_id or self.company_id.account_vninvoice_serial_id

    def get_account_vninvoice_type(self):
        return self.account_vninvoice_type_id or self.company_id.account_vninvoice_type_id

    @api.depends('account_vninvoice_serial_id')
    def _compute_account_vninvoice_template_id(self):
        for r in self:
            r.account_vninvoice_template_id = False
            if r.account_vninvoice_serial_id:
                if r.account_vninvoice_serial_id.template_id:
                    r.account_vninvoice_template_id = r.account_vninvoice_serial_id.template_id

    @api.depends('account_vninvoice_template_id')
    def _compute_account_vninvoice_type_id(self):
        for r in self:
            r.account_vninvoice_type_id = False
            if r.account_vninvoice_template_id:
                if r.account_vninvoice_template_id.type_id:
                    r.account_vninvoice_type_id = r.account_vninvoice_template_id.type_id