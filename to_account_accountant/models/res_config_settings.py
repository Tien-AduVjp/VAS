from datetime import date

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _prepare_transfer_account_domain(self):
        """
        Hook method to prepare transfer account domain
        """
        domain = [
            ('reconcile', '=', True),
            ('user_type_id.id', '=', self.env.ref('account.data_account_type_current_assets').id)
        ]
        return domain
    
    fiscalyear_last_day = fields.Integer(related='company_id.fiscalyear_last_day', required=True, readonly=False)
    fiscalyear_last_month = fields.Selection(related='company_id.fiscalyear_last_month', required=True, readonly=False)
    period_lock_date = fields.Date(string='Lock Date for Non-Advisers',
                                   related='company_id.period_lock_date', readonly=False)
    fiscalyear_lock_date = fields.Date(string='Lock Date for All Users',
                                       related='company_id.fiscalyear_lock_date', readonly=False)
    tax_lock_date = fields.Date("Tax Lock Date", related='company_id.tax_lock_date', readonly=False)
    use_anglo_saxon = fields.Boolean(string='Use Anglo-Saxon Accounting', related='company_id.anglo_saxon_accounting', readonly=False)
    transfer_account_id = fields.Many2one('account.account', string="Transfer Account",
        related='company_id.transfer_account_id', readonly=False,
        domain=_prepare_transfer_account_domain, help="This account used to transfer from liquidity to another.")
    
    @api.constrains('fiscalyear_last_day', 'fiscalyear_last_month')
    def _check_fiscalyear(self):
        # We do not define the constrain on res.company model while the recomputation
        # of the related fields is done one field at a time.
        for r in self:
            try:
                # test if the date exists in 2020 which is a leap year
                date(2020, int(r.fiscalyear_last_month), r.fiscalyear_last_day)
            except ValueError:
                raise ValidationError(
                    _('Incorrect fiscal year date: day is out of range for month. Month: %s; Day: %s') %
                    (r.fiscalyear_last_month, r.fiscalyear_last_day)
                )
