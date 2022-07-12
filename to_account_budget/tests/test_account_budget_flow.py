import datetime

from odoo.fields import Date
from odoo.tests.common import tagged

from .common import TestAccountBudgetCommon


@tagged('post_install', '-at_install')
class TestAccountBudgetFlow(TestAccountBudgetCommon):

    def test_01_account_budget_flow(self):

        # Creating a crossovered.budget record
        date_from = Date.from_string('%s-01-01' % (datetime.datetime.now().year + 1))
        date_to = Date.from_string('%s-12-31' % (datetime.datetime.now().year + 1))
        budget = self._create_crossovered_budget(date_from, date_to)

        # I created two different budget lines
        # Modifying a crossovered.budget record
        self._create_crossovered_budget_line(
            budget,
            date_from,
            date_to,
            10000,
            analytic_account=self.env.ref('analytic.analytic_partners_camp_to_camp'),
            general_budget=self.account_budget_post_purchase0
            )
        self._create_crossovered_budget_line(
            budget,
            Date.from_string('%s-09-01' % (datetime.datetime.now().year + 1)),
            Date.from_string('%s-09-30' % (datetime.datetime.now().year + 1)),
            400000,
            analytic_account=self.env.ref('analytic.analytic_our_super_product'),
            general_budget=self.account_budget_post_sales0
            )
        # I check that Initially Budget is in "draft" state
        self.assertEqual(budget.state, 'draft')

        # I pressed the confirm button to confirm the Budget
        # Performing an action confirm on module crossovered.budget
        budget.action_budget_confirm()

        # I check that budget is in "Confirmed" state
        self.assertEqual(budget.state, 'confirm')

        # I pressed the validate button to validate the Budget
        # Performing an action validate on module crossovered.budget
        budget.action_budget_validate()

        # I check that budget is in "Validated" state
        self.assertEqual(budget.state, 'validate')

        # I pressed the done button to set the Budget to "Done" state
        # Performing an action done on module crossovered.budget
        budget.action_budget_done()

        # I check that budget is in "done" state
        self.assertEqual(budget.state, 'done')
