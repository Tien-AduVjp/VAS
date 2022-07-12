from odoo import models, _
from odoo.exceptions import UserError


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def button_cancel_reconciliation(self):
        reconciles = self.env['employee.advance.reconcile'].sudo().search([
            ('state', 'in', ('confirm', 'done')),
            ('employee_id.address_home_id', 'in', self.journal_entry_ids.partner_id.ids)])
        for r in self:
            partner_reconciles = reconciles.filtered(
                lambda rec: rec.employee_id.sudo().address_home_id in r.journal_entry_ids.partner_id)
            for reconcile in partner_reconciles:
                move_lines = (reconcile.line_db_ids | reconcile.line_cr_ids).move_line_id
                for line in r.journal_entry_ids:
                    if line in move_lines:
                        raise UserError(_("You cannot revert reconciliation '%s' already contains journal items which has been link to a advance reconcile. "
                                          "Please delete journal items '%s' from the advance reconcile '%s' before.")
                                          % (r.name, line.name, reconcile.name))
        
        return super(AccountBankStatementLine, self).button_cancel_reconciliation()
