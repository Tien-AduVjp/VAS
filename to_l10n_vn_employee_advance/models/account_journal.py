import logging

from odoo import models, api, registry

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.onchange('is_advance_journal')
    def onchange_is_advance_journal(self):
        vn_chart_template_id = self.env.ref('l10n_vn.vn_template')
        if self.company_id.chart_template_id.id == vn_chart_template_id.id:
            if self.is_advance_journal:
                account_id = self.env['account.account'].search([('code', 'ilike', '141' + '%'), ('company_id', '=', self.company_id.id)], limit=1)
                if account_id:
                    self.default_debit_account_id = account_id
                    self.default_credit_account_id = account_id
            else:
                self.default_debit_account_id = self._origin and self._origin.default_debit_account_id or False
                self.default_credit_account_id = self._origin and self._origin.default_credit_account_id or False

    @api.model
    def update_employee_advance_journal_account(self):
        vn_chart_template_id = self.env.ref('l10n_vn.vn_template')
        if vn_chart_template_id:
            vn_company_ids = self.env['res.company'].search([('chart_template_id', '=', vn_chart_template_id.id)])
            for company_id in vn_company_ids:
                journals = self.env['account.journal'].search([('is_advance_journal', '=', True), ('company_id', '=', company_id.id)])
                account_id = self.env['account.account'].search([('code', 'ilike', '141' + '%'), ('company_id', '=', company_id.id)], limit=1)
                if account_id:
                    to_del_account_ids = journals.mapped('default_debit_account_id')
                    to_del_account_ids |= journals.mapped('default_credit_account_id')
                    journals.write({
                        'default_debit_account_id':account_id.id,
                        'default_credit_account_id':account_id.id,
                        })
                    for account_id in to_del_account_ids:
                        cr = registry(self._cr.dbname).cursor()
                        try:
                            account_id.with_env(account_id.env(cr=cr)).unlink()
                            cr.commit()
                        except Exception as e:
                            # rollback to avoid InternalError: current transaction is aborted, commands ignored until end of transaction block
                            cr.rollback()
                            _logger.error(e)
                        finally:
                            cr.close()

