from odoo import models, fields, api
from odoo.osv import expression

SHOW_BOTH_DR_CR_TRIAL_BALANCE_ACCOUNTS_DOMAIN = [
    '|', '|', '|', '|', '|', '|',
    ('code', '=like', '131%'),
    ('code', '=like', '138%'),
    ('code', '=like', '331%'),
    ('code', '=like', '333%'),
    ('code', '=like', '334%'),
    ('code', '=like', '338%'),
    ('code', '=like', '421%')
    ]


class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"

    @api.model
    def _get_show_both_dr_and_cr_trial_balance_domain(self):
        domain = super(AccountAccountTemplate, self)._get_show_both_dr_and_cr_trial_balance_domain()
        vn_template = self.env.ref('l10n_vn.vn_template', False)
        if vn_template:
            domain = expression.AND([
                domain,
                SHOW_BOTH_DR_CR_TRIAL_BALANCE_ACCOUNTS_DOMAIN,
                [('chart_template_id', '=', vn_template.id), ('show_both_dr_and_cr_trial_balance', '=', False)]
                ])
        return domain
