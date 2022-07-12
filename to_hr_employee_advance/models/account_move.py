from odoo import models, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_draft(self):
        self._validate_advance_reconcile_line()
        super(AccountMove, self).button_draft()

    def action_register_advance_payment(self):
        ''' Open the account.advance.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.advance.payment.register wizard.
        '''
        return {
            'name': _('Register Advance Payment'),
            'res_model': 'account.advance.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def _validate_advance_reconcile_line(self):
        advance_reconcile_lines = self.env['employee.advance.reconcile.line'].sudo().search([
            ('move_line_id', 'in', self.line_ids.ids)
        ])
        for r in self:
            to_check = advance_reconcile_lines.filtered(lambda a: a.move_line_id.id in r.line_ids.ids)
            if to_check:
                raise ValidationError(_("You cannot set journal entry %s to draft"
                                        " because it linked to Employee Advance Reconcile %s."
                                        " You must delete Employee Advance Reconcile %s first.")
                                        % (r.name, to_check[0].name, to_check[0].name))

            if r.payment_id and r.payment_id.employee_advance_id:
                if r.payment_id.employee_advance_id.state == 'done':
                    raise ValidationError(_("You cannot set payment %s to draft because it linked to Reconciled Employee Advance %s.")
                                            % (r.name, r.employee_advance_id.name))

            if r.payment_id and r.payment_id.employee_advance_reconcile_id:
                if r.payment_id.employee_advance_reconcile_id.state == 'done':
                    raise ValidationError(_("You cannot set payment %s to draft because it linked to Employee Advance Reconcile %s."
                                            " You must delete Employee Advance Reconcile %s first.")
                                            % (r.name, r.payment_id.employee_advance_reconcile_id.name, r.payment_id.employee_advance_reconcile_id.name))
