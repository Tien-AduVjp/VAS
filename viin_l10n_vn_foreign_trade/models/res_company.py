from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit='res.company'

    @api.model
    def _default_import_tax_payment_term_id(self):
        return self.env.ref('viin_l10n_vn_foreign_trade.account_payment_term_275_net_days') or False

    @api.model
    def _default_export_tax_payment_term_id(self):
        return self.env.ref('viin_l10n_vn_foreign_trade.account_payment_term_275_net_days') or False


    import_vat_ctp_account_id = fields.Many2one('account.account',
                                                string="Importing VAT Counter Part Account",
                                                help='The counter account for Importing VAT')
    import_tax_payment_term_id = fields.Many2one('account.payment.term',
                                              default=_default_import_tax_payment_term_id,
                                              string='Default Import Tax Payment Term')

    export_vat_ctp_account_id = fields.Many2one('account.account',
                                                string="Exporting VAT Counter Part Account",
                                                help='The counter account for Exporting VAT')
    export_tax_payment_term_id = fields.Many2one('account.payment.term',
                                              default=_default_export_tax_payment_term_id,
                                              string='Default Export Tax Payment Term')

    @api.model
    def set_default_settings(self):
        """
        Called upon new instasllation only
        """
        companies = self.search([])
        for company in companies:
            import_vat_ctp_account_id = company.property_vat_ctp_account_id
            import_tax_payment_term_id = company._default_import_tax_payment_term_id()
            export_vat_ctp_account_id = company.property_vat_ctp_account_id
            export_tax_payment_term_id = company._default_export_tax_payment_term_id()
            vals = {
                'import_vat_ctp_account_id': import_vat_ctp_account_id and import_vat_ctp_account_id.id or False,
                'import_tax_payment_term_id': import_tax_payment_term_id and import_tax_payment_term_id.id or False,
                'export_vat_ctp_account_id': export_vat_ctp_account_id and export_vat_ctp_account_id.id or False,
                'export_tax_payment_term_id': export_tax_payment_term_id and export_tax_payment_term_id.id or False,
                }
            company.write(vals)
