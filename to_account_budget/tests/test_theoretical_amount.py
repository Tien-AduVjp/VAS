import logging

from odoo.fields import Datetime, Date
from datetime import datetime, timedelta
from odoo.tests.common import tagged

from .common import TestAccountBudgetCommon
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestTheoreticalAmount(TestAccountBudgetCommon):
    def setUp(self):
        super(TestTheoreticalAmount, self).setUp()
        # create the budgetary position
        user_type_id = self.ref('account.data_account_type_revenue')
        tag_id = self.ref('account.account_tag_operating')
        account_rev = self.env['account.account'].create({
            'code': 'Y2020',
            'name': 'Budget - Test Revenue Account',
            'user_type_id': user_type_id,
            'tag_ids': [(4, tag_id, 0)]
        })
        buget_post = self.env['account.budget.post'].create({
            'name': 'Sales',
            'account_ids': [(4, account_rev.id, 0)],
        })
        # create the budget and budget lines
        first_january = Datetime.now().replace(day=1, month=1)
        self.last_day_of_budget = first_january + timedelta(days=364)  # will be 30th of December or 31th in case of leap year

        date_from = first_january.date()
        date_to = self.last_day_of_budget.date()

        crossovered_budget = self._create_crossovered_budget(date_from, date_to)

        self.line = self._create_crossovered_budget_line(
            crossovered_budget,
            date_from,
            date_to,
            -365,
            general_budget=buget_post
            )
        self.paid_date_line = self._create_crossovered_budget_line(
            crossovered_budget,
            date_from,
            date_to,
            -365,
            paid_date=Date.today().replace(day=9, month=9),
            general_budget=buget_post
            )

        self.patcher = patch('odoo.addons.to_account_budget.models.crossovered_budget.fields.Date', wraps=Date)
        self.mock_date = self.patcher.start()

    def test_01_theoretical_amount_without_paid_date(self):
        test_list = [
            (str(datetime.now().year) + '-01-01', -1),
            (str(datetime.now().year) + '-01-02', -2),
            (str(datetime.now().year) + '-01-03', -3),
            (str(datetime.now().year) + '-01-11', -11),
            (str(datetime.now().year) + '-02-20', -51),
            (str(self.last_day_of_budget.date()), -365),
        ]
        for date, expected_amount in test_list:
            _logger.info("Checking theoretical amount for the date: " + date)
            self.mock_date.today.return_value = Date.from_string(date)
            self.assertAlmostEqual(self.line.theoretical_amount, expected_amount)
            # invalidate the cache of the budget lines to recompute the theoretical amount at next iteration
            self.line.invalidate_cache()

    def test_02_theoretical_amount_with_paid_date(self):
        test_list = [
            (str(datetime.now().year) + '-01-01', 0),
            (str(datetime.now().year) + '-01-02', 0),
            (str(datetime.now().year) + '-09-08', 0),
            (str(datetime.now().year) + '-09-09', 0),
            (str(datetime.now().year) + '-09-10', -365),
            (str(self.last_day_of_budget.date()), -365),
        ]
        for date, expected_amount in test_list:
            _logger.info("Checking theoretical amount for the date: " + date)
            self.mock_date.today.return_value = Date.from_string(date)
            self.assertAlmostEqual(self.paid_date_line.theoretical_amount, expected_amount)
            # invalidate the cache of the budget lines to recompute the theoretical amount at next iteration
            self.paid_date_line.invalidate_cache()

    def tearDown(self):
        self.patcher.stop()
        super(TestTheoreticalAmount, self).tearDown()
