from odoo import models, _
from odoo.exceptions import ValidationError


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    def _prepare_unreconciled_move_lines_domain(self, reconciled_line_ids, date, company, journal_id=None):
        self.ensure_one()
        if journal_id and journal_id.company_id.id != company.id:
            raise ValidationError(_("Journal is invalid! Journal %s does not belong to company %s.")
                                  % (journal_id.name, company.name))
        domain = [
            ('partner_id', '=', self.sudo().address_home_id.id),
            ('account_id', '=', self.property_advance_account_id.id),
            ('parent_state', '=', 'posted'),
            ('id', 'not in', tuple(reconciled_line_ids)),
            ('date', '<=', date),
            ('reconciled', '=', False),
            ('company_id', '=', company.id)
        ]
        if journal_id:
            domain += [('journal_id', '=', journal_id.id)]
        return domain

    def _check_employee_unreconciled_advance(self, date, company, journal_id=None):
        self.ensure_one()
        reconciled_line_ids = []
        reconciles = self.env['employee.advance.reconcile'].search([
            ('company_id', '=', company.id),
            ('state', 'in', ('confirm', 'done'))
        ])
        if reconciles:
            # 1. Get line of move in payment
            reconciled_line_ids += reconciles.payment_ids.move_id.line_ids.filtered(
                lambda ml: ml.account_id.id == self.property_advance_account_id.id
            ).ids
            # 2. Get debit line in reconcile
            reconciled_line_ids += reconciles.line_db_ids.move_line_id.ids
            # 3. Get credit line in reconcile
            reconciled_line_ids += reconciles.line_cr_ids.move_line_id.ids

        unreconciled_move_lines_domain = self._prepare_unreconciled_move_lines_domain(reconciled_line_ids, date, company, journal_id)
        unreconciled_move_lines = self.env['account.move.line'].search(unreconciled_move_lines_domain)
        if unreconciled_move_lines:
            return True
        return False
