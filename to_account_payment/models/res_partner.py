from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    def _get_not_full_reconciled_account_move_lines_domain(self, company=None):
        self.ensure_one()
        company = company or self.company_id or self.env.company
        return [
            ('account_id.reconcile', '=', True),
            ('amount_residual', '!=', 0.0),
            ('partner_id', '=', self.id),
            ('company_id', '=', company.id),
            ('parent_state', '=', 'posted')
            ]

    def _get_not_full_reconciled_account_move_lines(self, company=None):
        self.ensure_one()
        return self.env['account.move.line'].search(self._get_not_full_reconciled_account_move_lines_domain(company))
    
