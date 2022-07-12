from odoo import fields
from odoo.tests.common import Form, tagged

from .common import TestAccountBudgetCommon


@tagged('post_install', '-at_install')
class TestAccountBudgetForm(TestAccountBudgetCommon):

    def test_01_account_budget_form(self):
        # Test: automated fill date_from and date_to on crossovered.budget.line
        budget_form = Form(self.env['crossovered.budget'])
        budget_form.date_from = fields.Date.to_date('2021-01-01')
        budget_form.date_to = fields.Date.to_date('2021-12-31')
        with budget_form.crossovered_budget_line_ids.new() as line_form:
            line_form.planned_amount = 365
            self.assertEqual(fields.Date.to_date(line_form.date_from), budget_form.date_from)
            self.assertEqual(fields.Date.to_date(line_form.date_to), budget_form.date_to)
