from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    general_employee_payable_account_id = fields.Many2one('account.account', string='General Employee Payable Account',
        help="A payable account for encoding employee payable accounting entries (e.g. in payslip batch mode or in case no payable account specified for the related employee)")

    def _generate_general_employee_payable_account(self):
        """
        Hook method for other localization modules to apply its own Employee Advance Account
        """
        pass
