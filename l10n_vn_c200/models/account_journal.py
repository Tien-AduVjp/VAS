from odoo import models, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.model
    def _prepare_liquidity_account(self, name, company, currency_id, type):
        res = super(AccountJournal, self)._prepare_liquidity_account(name, company, currency_id, type)
        if company.chart_template_id == self.env.ref('l10n_vn.vn_template'):
            code_prefix = res['code'][0]
            if code_prefix == '1':
                res['group_id'] = self.env.ref('l10n_vn_c200.acc_group_1').id
            elif code_prefix == '9':
                res['group_id'] = self.env.ref('l10n_vn_c200.acc_group_9').id

            code_prefix = res['code'][:3]
            if code_prefix == '111':
                res['tag_ids'] = [(6, 0, [self.env.ref('l10n_vn_c200.account_tag_111').id])]
            elif code_prefix == '112':
                res['tag_ids'] = [(6, 0, [self.env.ref('l10n_vn_c200.account_tag_112').id])]
        return res

