from datetime import datetime, date
from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class ExecutiveSummary(Common):

    def setUp(self):
        super(ExecutiveSummary, self).setUp()
        self.AccountExecutiveSummary = self.env.ref('to_account_reports.af_dynamic_report_executivesummary0')

    def test_01_validate_executive_summary(self):
        # 01/01/2021 Capital contribution 70000 cash
        journal_items_1 = [{
            'account_id': self.default_account_capital.id,
            'debit': 0,
            'credit': 70000,
        },
        {
            'account_id': self.default_account_cash.id,
            'debit': 70000,
            'credit': 0,
        }]
        journal_entry_1 = self._init_journal_entry(None , datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_1)

        # 01/01/2021 Buy fixed asset 50000 cash
        journal_items_2 = [{
            'account_id': self.default_account_cash.id,
            'debit': 0,
            'credit': 50000,
        },
        {
            'account_id': self.default_account_fixed_assets.id,
            'debit': 50000,
            'credit': 0,
        }]
        journal_entry_2_vendor_a = self._init_journal_entry(self.vendor_a , datetime(2021, 1, 1, 12, 0), self.default_journal_purchase, items=journal_items_2)

        # 01/01/2021 Uncollected sales (equipment) totaled 5000, with a record cost of equipment of 3000.
        journal_items_3 = [{
            'account_id': self.default_account_receivable.id,
            'debit': 5000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_revenue.id,
            'debit': 0,
            'credit': 5000,
        },
        {
            'account_id': self.default_account_type_direct_cost.id,
            'debit': 3000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_stock_delivered.id,
            'debit': 0,
            'credit': 3000,
        }]
        journal_entry_3 = self._init_journal_entry(self.customer_a , datetime(2021, 1, 1, 12, 0), self.default_journal_sale, items=journal_items_3)

        # 01/01/2021 Pay a salary 1000
        journal_items_4 = [{
            'account_id': self.default_account_cash.id,
            'debit': 0,
            'credit': 1000,
        },
        {
            'account_id': self.default_account_salary_expenses.id,
            'debit': 1000,
            'credit': 0,
        }]
        journal_entry_4 = self._init_journal_entry(None , datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_4)

        """
        Line Items                                               | 2021      |
        ---------------------------------------------------------|-----------|
        CASH                                                     |           |
        ---------------------------------------------------------|-----------|
        Cash received                                            | 70000     |
        Cash spent                                               | -51000    |
        Cash surplus                                             | 19000     |
        Closing bank balance                                     | 19000     |
        ---------------------------------------------------------|-----------|
        PROFITABILITY                                            |           |
        ---------------------------------------------------------|-----------|
        Income                                                   | 2000      |
        Cost of Revenue                                          | 3000      |
        ---------------------------------------------------------|-----------|
        Gross profit                                             | 2000      |
        ---------------------------------------------------------|-----------|
        Expenses                                                 | 1000      |
        Net Profit                                               | 1000      |
        ---------------------------------------------------------|-----------|
        BALANCE SHEET                                            |           |
        ---------------------------------------------------------|-----------|
        Receivables                                              | 5000      |
        Payables                                                 |           |
        Net assets                                               | 71000     |
        ---------------------------------------------------------|-----------|
        PERFORMANCE                                              |           |
        ---------------------------------------------------------|-----------|
        Gross profit margin (gross profit / operating income)    | 40        |
        Net profit margin (net profit / income)                  | 50        |
        Return on investments (net profit / assets)              | 1.4       |
        POSITION                                                 |           |
        Average debtors days                                     | 364       |
        Average creditors days                                   | 0         |
        Short term cash forecast                                 | 5000      |
        Current assets to liabilities                            | 0         |
        ---------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountExecutiveSummary, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('CASH', 0),
            ('Cash received', 70000),
            ('Cash spent', -51000),
            ('Cash surplus', 19000),
            ('Closing bank balance', 19000),
            ('PROFITABILITY', 0),
            ('Income', 2000),
            ('Cost of Revenue', 3000),
            ('Gross profit', 2000),
            ('Expenses', 1000),
            ('Net Profit', 1000),
            ('BALANCE SHEET', 0),
            ('Receivables', 5000),
            ('Payables', 0),
            ('Net assets', 71000),
            ('PERFORMANCE', 0),
            ('''Gross profit margin (gross profit / operating
\t\t\t\tincome)
\t\t\t''', 40),
            ('Net profit margin (net profit / income)', 50),
            ('Return on investments (net profit / assets)', 1.4),
            ('POSITION', 0),
            ('Average debtors days', 364),
            ('Average creditors days', 0),
            ('Short term cash forecast', 5000),
            ('Current assets to liabilities', 0),
        ]
        self._check_report_value(lines, table_value)
