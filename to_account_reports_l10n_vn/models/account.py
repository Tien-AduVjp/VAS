# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.osv import expression

from .account_account_template import SHOW_BOTH_DR_CR_TRIAL_BALANCE_ACCOUNTS_DOMAIN


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.model
    def _get_show_both_dr_and_cr_trial_balance_domain(self):
        domain = super(AccountAccount, self)._get_show_both_dr_and_cr_trial_balance_domain()
        vn_template = self.env.ref('l10n_vn.vn_template', False)
        if vn_template:
            domain = expression.AND([
                domain,
                SHOW_BOTH_DR_CR_TRIAL_BALANCE_ACCOUNTS_DOMAIN,
                [('company_id.chart_template_id', '=', vn_template.id), ('show_both_dr_and_cr_trial_balance', '=', False)]
                ])
        return domain
