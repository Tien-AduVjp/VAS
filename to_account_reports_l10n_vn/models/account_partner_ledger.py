from odoo import models


class AccountParnerLedger(models.AbstractModel):
    _inherit = 'account.partner.ledger'

    def get_templates(self):
        templates = super(AccountParnerLedger, self).get_templates()
        templates['render_print_template'] = 'to_account_reports_l10n_vn.template_partner_ledger_report_print_vn'
        return templates
