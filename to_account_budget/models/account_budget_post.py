from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


# ---------------------------------------------------------
# Budgetary Positions
#
# A Budgetary Position is an Odoo document that contains the general accounts for which you want
# to keep budgets (typically expense or income accounts). They need to be defined so Odoo can know
# which accounts it needs to go get the budget information. Some might be already installed with
# your chart of accounts
#
# For example, we need to define what accounts relates to a project's expenses,"
# just create a new position and add items of several expense accounts
# ---------------------------------------------------------
class AccountBudgetPost(models.Model):
    _name = 'account.budget.post'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name"
    _description = "Budgetary Position"

    name = fields.Char('Name', required=True, translate=True)
    account_ids = fields.Many2many('account.account', 'account_budget_rel', 'budget_id', 'account_id', string='Accounts',
                                   domain=[('deprecated', '=', False)],
                                   help="The general accounts for which you want to keep budgets (typically expense or income accounts)."
                                   " They need to be defined so Odoo can know which accounts it needs to go get the budget information.")
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)

    @api.constrains('account_ids', 'company_id')
    def _check_accounts_vs_company(self):
        for r in self:
            for account_id in r.account_ids:
                if account_id.company_id != r.company_id:
                    raise ValidationError(_("The account '%s' does not belong to the company %s")
                                          % (account_id.display_name, r.company_id.name))

    def _check_account_ids(self, vals):
        # Raise an error to prevent the account.budget.post to have not specified account_ids.
        # This check is done on create because require=True doesn't work on Many2many fields.
        if 'account_ids' in vals:
            account_ids = self.resolve_2many_commands('account_ids', vals['account_ids'])
        else:
            account_ids = self.account_ids
        if not account_ids:
            raise ValidationError(_('The budget must have at least one account.'))

    def _prepare_analytic_lines_domain(self):
        return [('general_account_id', 'in', self.account_ids.ids)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_account_ids(vals)
        return super(AccountBudgetPost, self).create(vals_list)

    def write(self, vals):
        self._check_account_ids(vals)
        return super(AccountBudgetPost, self).write(vals)
