from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class account_account(models.Model):
    _inherit = 'account.account'

    @api.model
    def remove_acc_999999(self):
        vn_chart_id = self.env.ref('l10n_vn.vn_template').id
        Account = self.env['account.account']
        for company in self.env['res.company'].search([('chart_template_id', '=', vn_chart_id)]):
            acc_999999_id = Account.search([('code', '=', '999999'), ('company_id', '=', company.id)])
            if acc_999999_id:
                acc_999999_id.unlink()
