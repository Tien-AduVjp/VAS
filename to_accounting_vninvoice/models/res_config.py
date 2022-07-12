from odoo import models, fields, api

class VNinvoiceConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    vninvoice_mode = fields.Selection(related='company_id.vninvoice_mode', readonly=False)
    vninvoice_start_date = fields.Date(related='company_id.vninvoice_start_date', readonly=False)
    vninvoice_api_url = fields.Char(related='company_id.vninvoice_api_url', readonly=False)
    sandbox_vninvoice_api_url = fields.Char(related='company_id.sandbox_vninvoice_api_url', readonly=False)

    account_vninvoice_serial_id = fields.Many2one(related='company_id.account_vninvoice_serial_id', readonly=False)
    account_vninvoice_template_id = fields.Many2one(related='company_id.account_vninvoice_template_id', readonly=False)
    account_vninvoice_type_id = fields.Many2one(related='company_id.account_vninvoice_type_id', readonly=False)
    vninvoice_api_username = fields.Char(related='company_id.vninvoice_api_username', readonly=False)
    vninvoice_api_password = fields.Char(related='company_id.vninvoice_api_password', readonly=False)

    def button_get_vninvoice_api_token(self):
        return self.company_id.get_vninvoice_api_token()

    @api.onchange('account_vninvoice_serial_id')
    def _onchange_account_vninvoice_serial(self):
        if self.account_vninvoice_serial_id:
            if self.account_vninvoice_serial_id.template_id:
                self.account_vninvoice_template_id = self.account_vninvoice_serial_id.template_id

    @api.onchange('account_vninvoice_template_id')
    def _onchange_account_vninvoice_template(self):
        if self.account_vninvoice_template_id:
            if self.account_vninvoice_template_id.type_id:
                self.account_vninvoice_type_id = self.account_vninvoice_template_id.type_id
