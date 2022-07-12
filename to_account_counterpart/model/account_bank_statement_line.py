from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'


    def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
        counterpart_moves = super(AccountBankStatementLine, self).process_reconciliation(counterpart_aml_dicts, payment_aml_rec, new_aml_dicts)
        counterpart_moves.action_smart_create_counterpart()
        return counterpart_moves
