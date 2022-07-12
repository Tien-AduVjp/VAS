from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from .common import TestAccountBudgetCommon


@tagged('post_install', '-at_install')
class TestAccountBudgetPeriod(TestAccountBudgetCommon):

    def test_01_period_of_account_budget_line(self):
        # Test: period of account budget line versus period of account budget
        date_from = fields.Date.to_date('2021-01-01')
        date_to = fields.Date.to_date('2021-12-31')
        budget = self._create_crossovered_budget(date_from, date_to, posted_items_only=False)

        # Case 1: account budget line from 31/12/2020 to 01/01/2021
        with self.assertRaises(ValidationError):
            self._create_crossovered_budget_line(
                budget,
                fields.Date.to_date('2020-12-31'),
                fields.Date.to_date('2021-01-01'),
                100000000)

        # Case 2: account budget line from 01/01/2021 to 01/01/2022
        with self.assertRaises(ValidationError):
            self._create_crossovered_budget_line(
                budget,
                fields.Date.to_date('2021-01-01'),
                fields.Date.to_date('2022-01-01'),
                100000000)

        # Case 3: account budget line from 01/01/2022 to 01/01/2021
        with self.assertRaises(ValidationError):
            self._create_crossovered_budget_line(
                budget,
                fields.Date.to_date('2022-01-01'),
                fields.Date.to_date('2021-01-01'),
                100000000)

        # Case 4: account budget line from 01/01/2020 to 31/12/2020
        with self.assertRaises(ValidationError):
            self._create_crossovered_budget_line(
                budget,
                fields.Date.to_date('2020-01-01'),
                fields.Date.to_date('2020-12-31'),
                100000000)

        # Case 5: account budget line from 01/01/2021 to 05/05/2021
        self._create_crossovered_budget_line(
            budget,
            fields.Date.to_date('2021-01-01'),
            fields.Date.to_date('2021-05-05'),
            100000000)

        # Case 6: account budget line from 04/05/2021 to 31/12/2021
        self._create_crossovered_budget_line(
            budget,
            fields.Date.to_date('2021-05-04'),
            fields.Date.to_date('2021-12-31'),
            100000000)
