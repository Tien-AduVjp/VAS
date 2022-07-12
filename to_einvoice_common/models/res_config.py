from odoo import models, fields

class EinvoiceConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    
    einvoice_provider = fields.Selection(string='E-Invoice Provider', related='company_id.einvoice_provider', readonly=False)
    einvoice_lock_legal_number = fields.Boolean(related='company_id.einvoice_lock_legal_number', readonly=False)
    einvoice_issue_earliest_invoice_first = fields.Boolean(related='company_id.einvoice_issue_earliest_invoice_first', readonly=False)
    # TODO: need to rename fields in version 14.0
    sinvoice_exchange_file_as_attachment = fields.Boolean(related='company_id.sinvoice_exchange_file_as_attachment', readonly=False)
    sinvoice_representation_file_as_attachment = fields.Boolean(related='company_id.sinvoice_representation_file_as_attachment', readonly=False)
    einvoice_auto_issue = fields.Boolean(related='company_id.einvoice_auto_issue', readonly=False)
    einvoice_api_version = fields.Selection(related='company_id.einvoice_api_version', readonly=False)

    def button_show_einvoice_disabled_journals(self):
        self.ensure_one()
        journals = self.env['account.journal'].search([('company_id', '=', self.company_id.id), ('einvoice_disabled', '=', True)])
        action = self.env.ref('account.action_account_journal_form')
        result = action.read()[0]

        # reset context
        result['context'] = {}
        # choose the view_mode accordingly
        journals_count = len(journals)
        if journals_count != 1:
            result['domain'] = "[('id', 'in', %s)]" % str(journals.ids)
        elif journals_count == 1:
            res = self.env.ref('account.view_account_journal_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = journals.id
        return result
