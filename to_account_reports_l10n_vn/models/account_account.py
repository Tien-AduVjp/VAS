from odoo import models, api
from odoo.osv import expression

from .account_account_template import SHOW_BOTH_DR_CR_TRIAL_BALANCE_ACCOUNTS_DOMAIN


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def _get_show_both_dr_and_cr_trial_balance_domain(self):
        domain = super(AccountAccount, self)._get_show_both_dr_and_cr_trial_balance_domain()
        template_ids = []
        vn_template = self.env.ref('l10n_vn.vn_template', False)
        if vn_template:
            template_ids.append(vn_template.id)
        vn_template_c133 = self.env.ref('l10n_vn_c133.vn_template_c133', False)
        if vn_template_c133:
            template_ids.append(vn_template_c133.id)
        if template_ids:
            domain = expression.AND([
                domain,
                SHOW_BOTH_DR_CR_TRIAL_BALANCE_ACCOUNTS_DOMAIN,
                [('company_id.chart_template_id', 'in', template_ids), ('show_both_dr_and_cr_trial_balance', '=', False)]
                ])
        return domain
