from odoo import models, _
from odoo.osv import expression

class HRExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    def action_register_advance_payment(self):
        ''' Open the account.advance.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.advance.payment.register wizard.
        '''
        return {
            'name': _('Register Advance Payment'),
            'res_model': 'account.advance.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move.line',
                'active_ids': self.move_ids.line_ids.filtered_domain([
                    ('move_id.state', '=', 'posted'),
                    ('account_internal_type', '=', 'payable'),
                    ('amount_residual', '!=', 0),
                ]).ids,
                'default_employee_id': self.employee_id.id,
                'default_expense_sheet_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def _prepare_amount_residual_domain(self):
        domain = super(HRExpenseSheet, self)._prepare_amount_residual_domain()
        if self.employee_id.property_advance_account_id:
            domain = expression.AND([domain, [('account_id', '!=', self.employee_id.property_advance_account_id.id)]])
        return domain
