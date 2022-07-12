from odoo import models, fields, _
from odoo.exceptions import AccessDenied


class AccountChangeLockDate(models.TransientModel):
    _name = 'account.change.lock.date'
    _description = 'Wizard to change lock date'

    tax_lock_date = fields.Date(
        "Tax Lock Date",
        default=lambda self: self.env.company.tax_lock_date,
        help='No users can edit journal entries related to a tax prior and inclusive of this date.')
    period_lock_date = fields.Date(string='Lock Date for Non-Advisers', default=lambda self: self.env.company.period_lock_date,
        help='The accounts whose accounting dates are prior to or inclusive of this date can be edited only by users with Advisor Role.\
        For instance, this function can be used to lock a period inside an open fiscal year.')
    fiscalyear_lock_date = fields.Date(string='Lock Date for All Users', default=lambda self: self.env.company.fiscalyear_lock_date,
        help='All users are prohibited from editing accounts with dates prior to or inclusive of this date.. Can use it to lock fiscal year.')

    def change_lock_date(self):
        if not self.env.user.has_group('account.group_account_manager'):
            raise AccessDenied(_("Only users who are granted with the access group '%s' will be able to execute this action.")
                               % self.env.ref('account.group_account_manager').display_name
                               )
        self.env.company.sudo().write({
            'period_lock_date': self.period_lock_date,
            'fiscalyear_lock_date': self.fiscalyear_lock_date,
            'tax_lock_date': self.tax_lock_date,
        })
        return {'type': 'ir.actions.act_window_close'}
