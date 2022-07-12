from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # TODO remove is_advance_payment in 15.0. Because we do not create payment when pay invoice from employee advance.
    is_advance_payment = fields.Boolean(string='Employee Advance Payment?', compute='_compute_is_advance_payment')
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  readonly=True, states={'draft': [('readonly', False)]})
    employee_advance_id = fields.Many2one('employee.advance', string='Employee Advance')
    employee_advance_reconcile_id = fields.Many2one('employee.advance.reconcile', string='Employee Advance Reconcile')

    @api.depends('journal_id')
    def _compute_is_advance_payment(self):
        for r in self:
            if r.journal_id.is_advance_journal == True:
                r.is_advance_payment = True
            else:
                r.is_advance_payment = False

    def action_post(self):
        super(AccountPayment, self).action_post()
        for r in self:
            if r.employee_advance_reconcile_id:
                r._reconcile_employee_advance_reconcile()
                if r.currency_id.is_zero(r.employee_advance_reconcile_id.balance):
                    r.employee_advance_reconcile_id.write({'state':'done'})
                    r.employee_advance_reconcile_id._update_employee_advance_state('done')

    def _reconcile_employee_advance_reconcile(self):
        """
        Reconcile payment for Employee Advance Reconcile
        """
        for r in self:
            if not r.employee_advance_reconcile_id:
                return
            domain = [
                ('account_id', '=', r.employee_advance_reconcile_id.employee_id.property_advance_account_id.id),
                ('reconciled', '=', False)
            ]
            to_reconcile = (r.employee_advance_reconcile_id.line_db_ids.move_line_id |
                            r.employee_advance_reconcile_id.line_cr_ids.move_line_id) \
                            .filtered_domain(domain)

            to_reconcile |= r.move_id.line_ids.filtered_domain(domain)

            if to_reconcile:
                to_reconcile.reconcile()
