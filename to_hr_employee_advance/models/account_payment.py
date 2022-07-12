from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_advance_journal = fields.Boolean(string="Employee Advance Journal?", related='journal_id.is_advance_journal')
    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  readonly=False, states={'posted': [('readonly', True)],
                                                          'sent': [('readonly', True)],
                                                          'reconciled': [('readonly', True)],
                                                          'cancelled': [('readonly', True)]})
    destination_employee_id = fields.Many2one('hr.employee', string='Targeted Employee',
                                              readonly=False, states={'posted': [('readonly', True)],
                                                                      'sent': [('readonly', True)],
                                                                      'reconciled': [('readonly', True)],
                                                                      'cancelled': [('readonly', True)]})
    require_dest_employee = fields.Boolean(string="Targeted Employee Required", related='destination_journal_id.is_advance_journal',
                                           help="Technical field to indicate if the targeted employee should be required.")
    employee_advance_id = fields.Many2one('employee.advance', string='Employee Advance')
    employee_advance_reconcile_id = fields.Many2one('employee.advance.reconcile', string='Employee Advance Reconcile')

    @api.onchange('destination_journal_id')
    def _onchange_destination_journal_id(self):
        if self.destination_journal_id.is_advance_journal:
            HREmployee = self.env['hr.employee']
            employee_id = HREmployee.search([('user_id', '=', self.env.user.id)], limit=1)
            if employee_id:
                self.destination_employee_id = employee_id

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id.is_advance_journal:
            HREmployee = self.env['hr.employee']
            employee_id = HREmployee.search([('user_id', '=', self.env.user.id)], limit=1)
            if employee_id:
                self.employee_id = employee_id

    @api.constrains('employee_id')
    def _constrain_employee_id(self):
        for r in self:
            if r.journal_id.is_advance_journal:
                if not r.employee_id:
                    raise UserError(_('You must select an Employee for Payment Method %s.') % r.journal_id.display_name)
                if not r.employee_id.sudo().address_home_id:
                    raise UserError(_('The selected employee %s does not have a Private Address yet. '
                                      'As usually, only employees with Private Address declared can participate accounting transactions.')
                                    % r.employee_id.name)
            if r.destination_journal_id and r.destination_journal_id.is_advance_journal:
                if not r.destination_employee_id:
                    raise UserError(_('You must select an Employee for Destination Payment Method %s.') % r.destination_journal_id.display_name)
                if not r.destination_employee_id.sudo().address_home_id:
                    raise UserError(_('The selected employee %s does not have a Private Address yet. '
                                      'As usually, only employees with Private Address declared can participate accounting transactions.')
                                    % r.destination_employee_id.name)

    def _prepare_payment_moves(self):
        all_move_vals = super(AccountPayment, self)._prepare_payment_moves()
        for r in self:
            if r.employee_advance_id and not r.employee_advance_id.company_id.use_employee_advance_pass_through_account:
                for move_vals in all_move_vals:
                    move_vals['line_ids'][0][2].update({
                        'name': r.employee_advance_id.name,
                        'partner_id': r.employee_advance_id.employee_id.sudo().address_home_id.id,
                        'account_id': r.employee_advance_id.journal_id.default_credit_account_id.id
                    })
            elif r.employee_advance_reconcile_id and not r.employee_advance_reconcile_id.employee_id.company_id.use_employee_advance_pass_through_account:
                for move_vals in all_move_vals:
                    move_vals['line_ids'][0][2].update({
                        'name': r.employee_advance_reconcile_id.name,
                        'partner_id': r.employee_advance_reconcile_id.employee_id.sudo().address_home_id.id,
                        'account_id': r.employee_advance_reconcile_id.journal_id.default_credit_account_id.id
                    })
            if r.journal_id.is_advance_journal and r.employee_id:
                for move_vals in all_move_vals:
                    # Liquidity line.
                    payment_id = move_vals['line_ids'][1][2].get('payment_id', 0)
                    if payment_id == r.id:
                        move_vals['line_ids'][1][2].update({
                            'partner_id': r.employee_id.sudo().address_home_id.id
                        })
        return all_move_vals

    def post(self):
        res = super(AccountPayment, self).post()
        for rec in self:
            precision = self.env['decimal.precision'].precision_get('Account')
            account_move_lines_to_reconcile = self.env['account.move.line']
            if rec.employee_advance_id and float_is_zero(rec.employee_advance_id.balance, precision_digits=precision):
                for line in rec.employee_advance_id.payment_ids.mapped('move_line_ids') + rec.employee_advance_id.move_id.line_ids:
                    if line.account_id.internal_type == 'payable':
                        account_move_lines_to_reconcile |= line
                if account_move_lines_to_reconcile:
                    account_move_lines_to_reconcile.auto_reconcile_lines()
                rec.employee_advance_id.write({'state':'spent'})
            elif rec.employee_advance_reconcile_id and float_is_zero(rec.employee_advance_reconcile_id.balance, precision_digits=precision):
                for line in rec.employee_advance_reconcile_id.payment_ids.mapped('move_line_ids') + rec.employee_advance_reconcile_id.move_id.line_ids:
                    if line.account_id.reconcile == True:
                        account_move_lines_to_reconcile |= line
                if account_move_lines_to_reconcile:
                    account_move_lines_to_reconcile.auto_reconcile_lines()
                rec.employee_advance_reconcile_id.write({'state':'done'})
                rec.employee_advance_reconcile_id._update_employee_advance_state('done')
        return res
    
    def action_draft(self):
        reconciles = self.env['employee.advance.reconcile'].search([
            ('state', 'in', ('confirm', 'done')),
            ('employee_id', 'in', self.filtered(lambda r: r.is_advance_journal).employee_id.ids)])
        for r in self:
            if r.is_advance_journal:
                employee_reconciles = reconciles.filtered(lambda r: r.employee_id.id == r.employee_id.id)
                for reconcile in employee_reconciles:
                    move_lines = (reconcile.line_db_ids | reconcile.line_cr_ids).move_line_id
                    if r.move_line_ids.filtered(lambda line: line in move_lines):
                        raise UserError(_("You cannot set to draft the payment '%s' that has been link to a advance reconcile. "
                                                "Please delete it from the advance reconcile '%s' before.")
                                          % (r.name, reconcile.name))
            elif r.employee_advance_id:
                if r.employee_advance_id.state == 'done':
                    raise UserError(_("You can not set to draft a payment of reconciled employee advance request."))
                for move in r.employee_advance_id.payment_ids.mapped('move_line_ids.move_id'):
                    move.line_ids.remove_move_reconcile()
                    r.employee_advance_id.write({'state':'validate'})
                    r.employee_advance_id = False
            elif r.employee_advance_reconcile_id:
                if r.employee_advance_reconcile_id.state == 'done':
                    raise UserError(_("You can not set to draft a payment of employee advance reconcile in 'Done' state."))
                for move in r.employee_advance_reconcile_id.payment_ids.mapped('move_line_ids.move_id'):
                    move.line_ids.remove_move_reconcile()
                    r.employee_advance_reconcile_id.write({'state':'confirm'})
                    r.employee_advance_reconcile_id._update_employee_advance_state('spent')
                    r.employee_advance_reconcile_id = False
        
        return super(AccountPayment, self).action_draft()


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
 
    is_advance_journal = fields.Boolean(string="Employee Advance Journal?", related='journal_id.is_advance_journal')
    employee_id = fields.Many2one('hr.employee', string="Employee")
 
    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id.is_advance_journal:
            HREmployee = self.env['hr.employee']
            employee_id = HREmployee.search([('user_id', '=', self.env.user.id)], limit=1)
            if employee_id:
                self.employee_id = employee_id
 
    def _prepare_payment_vals(self, invoices):
        res = super(AccountPaymentRegister, self)._prepare_payment_vals(invoices)
        if self.employee_id:
            res['employee_id'] = self.employee_id.id
        return res
