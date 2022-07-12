from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_users import parse_m2m


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
    _check_company_auto = True

    name = fields.Char('Name', required=True, translate=True)
    account_ids = fields.Many2many('account.account', 'account_budget_rel', 'budget_id', 'account_id', string='Accounts',
                                   domain="[('deprecated', '=', False),('company_id', '=', company_id)]",
                                   required=True, check_company=True,
                                   help="The general accounts for which you want to keep budgets (typically expense or income accounts)."
                                   " They need to be defined so Odoo can know which accounts it needs to go get the budget information.")
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)
    
    def _prepare_analytic_lines_domain(self):
        return [('general_account_id', 'in', self.account_ids.ids)]
