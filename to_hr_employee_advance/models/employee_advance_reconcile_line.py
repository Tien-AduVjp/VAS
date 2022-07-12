from odoo import models, fields


class HrEmployeeAdvanceReconcileLine(models.Model):
    _name = 'employee.advance.reconcile.line'
    _description = 'HR Employee Advance Reconcile Line'

    reconcile_id = fields.Many2one('employee.advance.reconcile',
                                   string='Reconcile', ondelete='cascade', index=True)
    name = fields.Char(string='Description', required=True, readonly=True)
    move_line_id = fields.Many2one('account.move.line',
                                   string='Journal Item', required=True, readonly=True, ondelete='cascade')
    account_id = fields.Many2one('account.account',
                                 string='Account', required=True, readonly=True)
    date = fields.Date(string='Date', required=True, readonly=True)
    amount = fields.Float(string='Amount', required=True, readonly=True, digits='Account')
    type = fields.Selection([
        ('db', 'Debit'),
        ('cr', 'Credit'),
    ], string='Type', required=True, readonly=True)
