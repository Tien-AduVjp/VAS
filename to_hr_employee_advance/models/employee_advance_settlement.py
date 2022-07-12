from odoo import fields, models


class HrEmployeeAdvanceSettlement(models.Model):
    _name = 'employee.advance.settlement'
    _description = 'HR Employee Advance Settlement'

    reconcile_id = fields.Many2one('employee.advance.reconcile', string="Reconcile", ondelete='cascade', index=True)
    name = fields.Char(string="Reference")
    reference = fields.Char(string="Reference")
    date = fields.Date(string="Date", required=True, default=fields.Date.today)
    amount = fields.Float(string="Amount", required=True, digits='Account')
    journal_id = fields.Many2one('account.journal',
                                 string="Settlement Method", required=True, domain=[('type', 'in', ('bank', 'cash'))])
    type = fields.Selection([
        ('pay', 'Pay'),
        ('refund', 'Refund'),
    ], string="Type")
    move_id = fields.Many2one('account.move', string="Journal Entry")

    def action_settle(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        move_obj = self.env['account.move']
        move_lines = []
        address_home = self.reconcile_id.employee_id.sudo().address_home_id
        if self.type == 'pay':
            move_lines.append((0, 0, {
                'name': self.name and self.name or '/',
                'partner_id': address_home.id,
                'account_id': self.journal_id.default_credit_account_id.id,
                'credit': self.amount,
            }))
            move_lines.append((0, 0, {
                'name': self.name and self.name or '/',
                'partner_id': address_home.id,
                'account_id': address_home.property_account_payable_id.id,
                'debit': self.amount
            }))
        elif self.type == 'refund':
            move_lines.append((0, 0, {
                'name': self.name and self.name or '/',
                'partner_id': address_home.id,
                'account_id': address_home.property_account_receivable_id.id,
                'credit': self.amount,
            }))
            move_lines.append((0, 0, {
                'name': self.name and self.name or '/',
                'partner_id': address_home.id,
                'account_id': self.journal_id.default_credit_account_id.id,
                'debit': self.amount
            }))

        move = move_obj.create({
            'journal_id': self.journal_id.id,
            'date': self.date,
            'ref': self.reference,
            'line_ids': move_lines,
        })
        move.post()
        self.write({'move_id':move.id})
        self.reconcile_id._get_amount()
        if self.reconcile_id.balance <= 0:
            self.reconcile_id.write({'state':'done'})
            self.reconcile_id._update_employee_advance_state('done')

            # Create full reconcile
            reconciled_line_ids = False
            move_line1 = self.reconcile_id.move_lines.filtered(lambda r: r.account_id.reconcile == True)
            if move_line1:
                reconciled_line_ids = move_line1[0]
                for sett in self.reconcile_id.settlement_ids:
                    for line in sett.move_id.line_ids.filtered(lambda r: r.account_id.reconcile == True):
                        reconciled_line_ids += line
                if len(reconciled_line_ids) > 1:
                    reconciled_line_ids.reconcile()

        return {'type': 'ir.actions.act_window_close'}
