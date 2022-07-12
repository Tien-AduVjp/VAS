from odoo import models, fields, api


class SinvoiceConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    sinvoice_mode = fields.Selection(related='company_id.sinvoice_mode', readonly=False)
    sinvoice_start = fields.Date(related='company_id.sinvoice_start', readonly=False)
    sinvoice_api_url = fields.Char(related='company_id.sinvoice_api_url', readonly=False)
    sandbox_sinvoice_api_url = fields.Char(related='company_id.sandbox_sinvoice_api_url', readonly=False)

    account_sinvoice_serial_id = fields.Many2one(related='company_id.account_sinvoice_serial_id', readonly=False)
    account_sinvoice_template_id = fields.Many2one(related='company_id.account_sinvoice_template_id', readonly=False)
    account_sinvoice_type_id = fields.Many2one(related='company_id.account_sinvoice_type_id', readonly=False)
    sinvoice_api_username = fields.Char(related='company_id.sinvoice_api_username', readonly=False)
    sinvoice_api_password = fields.Char(related='company_id.sinvoice_api_password', readonly=False)
    sinvoice_synch_payment_status = fields.Boolean(related='company_id.sinvoice_synch_payment_status', readonly=False)
    sinvoice_conversion_user_id = fields.Many2one(related='company_id.sinvoice_conversion_user_id', readonly=False)
    sinvoice_max_len_bank_name = fields.Integer(related='company_id.sinvoice_max_len_bank_name', readonly=False)
    sinvoice_max_len_bank_account = fields.Integer(related='company_id.sinvoice_max_len_bank_account', readonly=False)
    
    
    def button_get_sinvoice_status(self):
        return self.company_id.get_sinvoice_status()

    @api.onchange('account_sinvoice_serial_id')
    def _onchange_account_sinvoice_serial(self):
        if self.account_sinvoice_serial_id:
            if self.account_sinvoice_serial_id.template_id:
                self.account_sinvoice_template_id = self.account_sinvoice_serial_id.template_id

    @api.onchange('account_sinvoice_template_id')
    def _onchange_account_sinvoice_template(self):
        if self.account_sinvoice_template_id:
            if self.account_sinvoice_template_id.type_id:
                self.account_sinvoice_type_id = self.account_sinvoice_template_id.type_id

