from datetime import datetime, date
from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class GAAPReport(Common):

    def setUp(self):
        super(GAAPReport, self).setUp()
        self.AccountBalanceSheetReport = self.env.ref('to_account_reports.af_dynamic_report_balancesheet0')
        self.AccountProfitLossReport = self.env.ref('to_account_reports.af_dynamic_report_profitandloss0')
        self.AccountCashFlowReport = self.env.ref('to_account_reports.af_dynamic_report_cashsummary0')

    def test_01_validate_gaap_report(self):
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
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 70000       |
        Bank and Cash Accounts         | 70000       |
        Receivables                    |             |
        Current Assets                 |             |
        Prepayments                    |             |
        Plus Fixed Assets              |             |
        Plus Non-current Assets        |             |
        -------------------------------|-------------|
        ASSETS                         | 70000       |
        -------------------------------|-------------|
        Total Current Liabilities      |             |
        Current Liabilities            |             |
        Payables                       |             |
        Non-current Liabilities        |             |
        -------------------------------|-------------|
        LIABILITIES                    |             |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          |             |
        RETAINED EARNINGS              | 70000       |
        -------------------------------|-------------|
        EQUITY                         | 70000       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 70000),
            ('Bank and Cash Accounts', 70000),
            ('Receivables', 0),
            ('Current Assets', 0),
            ('Prepayments', 0),
            ('Plus Fixed Assets', 0),
            ('Plus Non-current Assets', 0),
            ('ASSETS', 70000),
            ('Total Current Liabilities', 0),
            ('Current Liabilities', 0),
            ('Payables', 0),
            ('Non-current Liabilities', 0),
            ('LIABILITIES', 0),
            ('CURRENT YEAR EARNINGS', 0),
            ('RETAINED EARNINGS', 70000),
            ('EQUITY', 70000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      |           |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            |           |
        Cash paid for operating activities                                            |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 70000     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 70000     |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 70000     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 70000     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 70000),
            ('Cash in', 70000),
            ('Cash out', 0),
            ('Net increase in cash and cash equivalents', 70000),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 70000),
        ]
        self._check_report_value(lines, table_value)

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
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 20000       |
        Bank and Cash Accounts         | 20000       |
        Receivables                    |             |
        Current Assets                 |             |
        Prepayments                    |             |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        |             |
        -------------------------------|-------------|
        ASSETS                         | 70000       |
        -------------------------------|-------------|
        Total Current Liabilities      |             |
        Current Liabilities            |             |
        Payables                       |             |
        Non-current Liabilities        |             |
        -------------------------------|-------------|
        LIABILITIES                    |             |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          |             |
        RETAINED EARNINGS              | 70000       |
        -------------------------------|-------------|
        EQUITY                         | 70000       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 20000),
            ('Bank and Cash Accounts', 20000),
            ('Receivables', 0),
            ('Current Assets', 0),
            ('Prepayments', 0),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 0),
            ('ASSETS', 70000),
            ('Total Current Liabilities', 0),
            ('Current Liabilities', 0),
            ('Payables', 0),
            ('Non-current Liabilities', 0),
            ('LIABILITIES', 0),
            ('CURRENT YEAR EARNINGS', 0),
            ('RETAINED EARNINGS', 70000),
            ('EQUITY', 70000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      |           |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            |           |
        Cash paid for operating activities                                            |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 20000     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 70000     |
        Cash out                                                                      | -50000    |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 20000     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 20000     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 20000),
            ('Cash in', 70000),
            ('Cash out', -50000),
            ('Net increase in cash and cash equivalents', 20000),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 20000),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 Create vendor bill 9000 for vendor a
        journal_items_3 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 9000,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_stock.id,
            'debit': 9000,
            'credit': 0,
        }]
        journal_entry_3_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 1, 1, 12, 0), self.default_journal_purchase, items=journal_items_3)
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 29000       |
        Bank and Cash Accounts         | 20000       |
        Receivables                    |             |
        Current Assets                 | 9000        |
        Prepayments                    |             |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        |             |
        -------------------------------|-------------|
        ASSETS                         | 79000       |
        -------------------------------|-------------|
        Total Current Liabilities      | 9000        |
        Current Liabilities            |             |
        Payables                       | 9000        |
        Non-current Liabilities        |             |
        -------------------------------|-------------|
        LIABILITIES                    | 9000        |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          |             |
        RETAINED EARNINGS              | 70000       |
        -------------------------------|-------------|
        EQUITY                         | 70000       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 29000),
            ('Bank and Cash Accounts', 20000),
            ('Receivables', 0),
            ('Current Assets', 9000),
            ('Prepayments', 0),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 0),
            ('ASSETS', 79000),
            ('Total Current Liabilities', 9000),
            ('Current Liabilities', 0),
            ('Payables', 9000),
            ('Non-current Liabilities', 0),
            ('LIABILITIES', 9000),
            ('CURRENT YEAR EARNINGS', 0),
            ('RETAINED EARNINGS', 70000),
            ('EQUITY', 70000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | 9000      |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      |           |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            | 9000      |
        Cash paid for operating activities                                            |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 11000     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 70000     |
        Cash out                                                                      | -59000    |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 20000     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 20000     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 20000),
            ('Cash in', 70000),
            ('Cash out', -50000),
            ('Net increase in cash and cash equivalents', 20000),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 20000),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 Create vendor payment 5000 for vendor a
        journal_items_4 = [{
            'account_id': self.default_account_cash.id,
            'debit': 0,
            'credit': 5000,
            'date_maturity': date(2021, 1, 1),
        },
        {
            'account_id': self.default_account_payable.id,
            'debit': 5000,
            'credit': 0,
            'date_maturity': date(2021, 1, 1),
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_4_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 1, 1, 12, 0), self.default_journal_cash  , items=journal_items_4)
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 24000       |
        Bank and Cash Accounts         | 15000       |
        Receivables                    |             |
        Current Assets                 | 9000        |
        Prepayments                    |             |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        |             |
        -------------------------------|-------------|
        ASSETS                         | 74000       |
        -------------------------------|-------------|
        Total Current Liabilities      | 4000        |
        Current Liabilities            |             |
        Payables                       | 4000        |
        Non-current Liabilities        |             |
        -------------------------------|-------------|
        LIABILITIES                    | 4000        |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          |             |
        RETAINED EARNINGS              | 70000       |
        -------------------------------|-------------|
        EQUITY                         | 70000       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 24000),
            ('Bank and Cash Accounts', 15000),
            ('Receivables', 0),
            ('Current Assets', 9000),
            ('Prepayments', 0),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 0),
            ('ASSETS', 74000),
            ('Total Current Liabilities', 4000),
            ('Current Liabilities', 0),
            ('Payables', 4000),
            ('Non-current Liabilities', 0),
            ('LIABILITIES', 4000),
            ('CURRENT YEAR EARNINGS', 0),
            ('RETAINED EARNINGS', 70000),
            ('EQUITY', 70000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | 4000      |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      |           |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 11000     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 70000     |
        Cash out                                                                      | -59000    |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 15000     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 15000     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 20000),
            ('Cash in', 70000),
            ('Cash out', -50000),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', -5000),
            ('Net increase in cash and cash equivalents', 15000),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 15000),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 Create customer payment 250 for customer a
        journal_items_5 = [{
            'account_id': self.default_account_receivable.id,
            'debit': 0,
            'credit': 250,
            'date_maturity': date(2021, 1, 1),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_cash.id,
            'debit': 250,
            'credit': 0,
            'date_maturity': date(2021, 1, 1),
        }]
        journal_entry_5 = self._init_journal_entry(self.customer_a, datetime(2021, 1, 1, 12, 0), self.default_journal_cash, items=journal_items_5)
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 24000       |
        Bank and Cash Accounts         | 15250       |
        Receivables                    | -250        |
        Current Assets                 | 9000        |
        Prepayments                    |             |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        |             |
        -------------------------------|-------------|
        ASSETS                         | 74000       |
        -------------------------------|-------------|
        Total Current Liabilities      | 4000        |
        Current Liabilities            |             |
        Payables                       | 4000        |
        Non-current Liabilities        |             |
        -------------------------------|-------------|
        LIABILITIES                    | 4000        |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          |             |
        RETAINED EARNINGS              | 70000       |
        -------------------------------|-------------|
        EQUITY                         | 70000       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 24000),
            ('Bank and Cash Accounts', 15250),
            ('Receivables', -250),
            ('Current Assets', 9000),
            ('Prepayments', 0),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 0),
            ('ASSETS', 74000),
            ('Total Current Liabilities', 4000),
            ('Current Liabilities', 0),
            ('Payables', 4000),
            ('Non-current Liabilities', 0),
            ('LIABILITIES', 4000),
            ('CURRENT YEAR EARNINGS', 0),
            ('RETAINED EARNINGS', 70000),
            ('EQUITY', 70000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | 4250      |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      | 250       |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 11000     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 70000     |
        Cash out                                                                      | -59000    |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 15250     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 15250     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 20000),
            ('Cash in', 70000),
            ('Cash out', -50000),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', -4750),
            ('Net increase in cash and cash equivalents', 15250),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 15250),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 Short-term bank loan 30000 for 12 months
        journal_items_6 = [{
            'account_id': self.default_account_current_liabilities.id,
            'debit': 0,
            'credit': 30000,
        },
        {
            'account_id': self.default_account_liquidity.id,
            'debit': 30000,
            'credit': 0,
        }]
        journal_entry_6 = self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_6)
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 54000       |
        Bank and Cash Accounts         | 45250       |
        Receivables                    | -250        |
        Current Assets                 | 9000        |
        Prepayments                    |             |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        |             |
        -------------------------------|-------------|
        ASSETS                         | 104000      |
        -------------------------------|-------------|
        Total Current Liabilities      | 34000       |
        Current Liabilities            | 30000       |
        Payables                       | 4000        |
        Non-current Liabilities        |             |
        -------------------------------|-------------|
        LIABILITIES                    | 34000       |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          |             |
        RETAINED EARNINGS              | 70000       |
        -------------------------------|-------------|
        EQUITY                         | 70000       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 54000),
            ('Bank and Cash Accounts', 45250),
            ('Receivables', -250),
            ('Current Assets', 9000),
            ('Prepayments', 0),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 0),
            ('ASSETS', 104000),
            ('Total Current Liabilities', 34000),
            ('Current Liabilities', 30000),
            ('Payables', 4000),
            ('Non-current Liabilities', 0),
            ('LIABILITIES', 34000),
            ('CURRENT YEAR EARNINGS', 0),
            ('RETAINED EARNINGS', 70000),
            ('EQUITY', 70000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | 4250      |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      | 250       |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 41000     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 100000    |
        Cash out                                                                      | -59000    |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 45250     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 45250     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 50000),
            ('Cash in', 100000),
            ('Cash out', -50000),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', -4750),
            ('Net increase in cash and cash equivalents', 45250),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 45250),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 Long-term bank loan 30000 for 36 months
        journal_items_7 = [{
            'account_id': self.default_account_non_current_liabilities.id,
            'debit': 0,
            'credit': 30000,
        },
        {
            'account_id': self.default_account_liquidity.id,
            'debit': 30000,
            'credit': 0,
        }]
        journal_entry_7 = self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_7)
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 84000       |
        Bank and Cash Accounts         | 75250       |
        Receivables                    | -250        |
        Current Assets                 | 9000        |
        Prepayments                    |             |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        |             |
        -------------------------------|-------------|
        ASSETS                         | 134000      |
        -------------------------------|-------------|
        Total Current Liabilities      | 34000       |
        Current Liabilities            | 30000       |
        Payables                       | 4000        |
        Non-current Liabilities        | 30000       |
        -------------------------------|-------------|
        LIABILITIES                    | 64000       |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          |             |
        RETAINED EARNINGS              | 70000       |
        -------------------------------|-------------|
        EQUITY                         | 70000       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 84000),
            ('Bank and Cash Accounts', 75250),
            ('Receivables', -250),
            ('Current Assets', 9000),
            ('Prepayments', 0),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 0),
            ('ASSETS', 134000),
            ('Total Current Liabilities', 34000),
            ('Current Liabilities', 30000),
            ('Payables', 4000),
            ('Non-current Liabilities', 30000),
            ('LIABILITIES', 64000),
            ('CURRENT YEAR EARNINGS', 0),
            ('RETAINED EARNINGS', 70000),
            ('EQUITY', 70000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | 4250      |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      | 250       |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 71000     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 130000    |
        Cash out                                                                      | -59000    |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 75250     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 75250     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 80000),
            ('Cash in', 130000),
            ('Cash out', -50000),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', -4750),
            ('Net increase in cash and cash equivalents', 75250),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 75250),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 To increase capital by selling shares 15000
        journal_items_8 = [{
            'account_id': self.default_account_capital.id,
            'debit': 0,
            'credit': 15000,
        },
        {
            'account_id': self.default_account_liquidity.id,
            'debit': 15000,
            'credit': 0,
        }]
        journal_entry_8 = self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_8)
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 99000       |
        Bank and Cash Accounts         | 90250       |
        Receivables                    | -250        |
        Current Assets                 | 9000        |
        Prepayments                    |             |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        |             |
        -------------------------------|-------------|
        ASSETS                         | 149000      |
        -------------------------------|-------------|
        Total Current Liabilities      | 34000       |
        Current Liabilities            | 30000       |
        Payables                       | 4000        |
        Non-current Liabilities        | 30000       |
        -------------------------------|-------------|
        LIABILITIES                    | 64000       |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          |             |
        RETAINED EARNINGS              | 85000       |
        -------------------------------|-------------|
        EQUITY                         | 85000       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 99000),
            ('Bank and Cash Accounts', 90250),
            ('Receivables', -250),
            ('Current Assets', 9000),
            ('Prepayments', 0),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 0),
            ('ASSETS', 149000),
            ('Total Current Liabilities', 34000),
            ('Current Liabilities', 30000),
            ('Payables', 4000),
            ('Non-current Liabilities', 30000),
            ('LIABILITIES', 64000),
            ('CURRENT YEAR EARNINGS', 0),
            ('RETAINED EARNINGS', 85000),
            ('EQUITY', 85000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | 4250      |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      | 250       |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 86000     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 145000    |
        Cash out                                                                      | -59000    |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 90250     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 90250     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 95000),
            ('Cash in', 145000),
            ('Cash out', -50000),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', -4750),
            ('Net increase in cash and cash equivalents', 90250),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 90250),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 Buy technical know-how for 50000, prepayment for 10000, and debt for 40000 over a 48-month period.
        journal_items_9 = [{
            'account_id': self.default_account_non_assets.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_liquidity.id,
            'debit': 0,
            'credit': 10000,
        },
        {
            'account_id': self.default_account_non_current_liabilities.id,
            'debit': 0,
            'credit': 40000,
        }]
        journal_entry_9 = self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_9)
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 89000       |
        Bank and Cash Accounts         | 80250       |
        Receivables                    | -250        |
        Current Assets                 | 9000        |
        Prepayments                    |             |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        | 50000       |
        -------------------------------|-------------|
        ASSETS                         | 189000      |
        -------------------------------|-------------|
        Total Current Liabilities      | 34000       |
        Current Liabilities            | 30000       |
        Payables                       | 4000        |
        Non-current Liabilities        | 70000       |
        -------------------------------|-------------|
        LIABILITIES                    | 104000      |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          |             |
        RETAINED EARNINGS              | 85000       |
        -------------------------------|-------------|
        EQUITY                         | 85000       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 89000),
            ('Bank and Cash Accounts', 80250),
            ('Receivables', -250),
            ('Current Assets', 9000),
            ('Prepayments', 0),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 50000),
            ('ASSETS', 189000),
            ('Total Current Liabilities', 34000),
            ('Current Liabilities', 30000),
            ('Payables', 4000),
            ('Non-current Liabilities', 70000),
            ('LIABILITIES', 104000),
            ('CURRENT YEAR EARNINGS', 0),
            ('RETAINED EARNINGS', 85000),
            ('EQUITY', 85000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | 4250      |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      | 250       |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 85000     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 185000    |
        Cash out                                                                      | -100000   |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 80250     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 80250     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 45000),
            ('Cash in', 145000),
            ('Cash out', -100000),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', 35250),
            ('Net increase in cash and cash equivalents', 80250),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 80250),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 Allocate the cost of employing technical know-how over a five-year period, at a rate of 10000 each year.
        journal_items_10 = [{
            'account_id': self.default_account_expense.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_non_assets.id,
            'debit': 0,
            'credit': 10000,
        }]
        journal_entry_10 = self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_10)
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 89000       |
        Bank and Cash Accounts         | 80250       |
        Receivables                    | -250        |
        Current Assets                 | 9000        |
        Prepayments                    |             |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        | 40000       |
        -------------------------------|-------------|
        ASSETS                         | 179000      |
        -------------------------------|-------------|
        Total Current Liabilities      | 34000       |
        Current Liabilities            | 30000       |
        Payables                       | 4000        |
        Non-current Liabilities        | 70000       |
        -------------------------------|-------------|
        LIABILITIES                    | 104000      |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          | -10000      |
        RETAINED EARNINGS              | 85000       |
        -------------------------------|-------------|
        EQUITY                         | 75000       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 89000),
            ('Bank and Cash Accounts', 80250),
            ('Receivables', -250),
            ('Current Assets', 9000),
            ('Prepayments', 0),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 40000),
            ('ASSETS', 179000),
            ('Total Current Liabilities', 34000),
            ('Current Liabilities', 30000),
            ('Payables', 4000),
            ('Non-current Liabilities', 70000),
            ('LIABILITIES', 104000),
            ('CURRENT YEAR EARNINGS', -10000),
            ('RETAINED EARNINGS', 85000),
            ('EQUITY', 75000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------------|
        |Expect value (Profit and Loss)|
        |------------------------------|
        Line items                     | 2021     |
        -------------------------------|----------|
        Total Income                   |          |
        -------------------------------|----------|
        Total Gross Profit             |          |
        Operating Income               |          |
        Financial Income               |          |
        Income Deduction               |          |
        Gross Income                   |          |
        Cost of Revenue                |          |
        Other Income                   |          |
        -------------------------------|----------|
        Total Expenses                 | 10000    |
        -------------------------------|----------|
        Expenses                       | 10000    |
        Depreciation                   |          |
        -------------------------------|----------|
        NET PROFIT                     | -10000   |
        -------------------------------|----------|
        """
        lines = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Income', 0),
            ('Total Gross Profit', 0),
            ('Operating Income', 0),
            ('Financial Income', 0),
            ('Income Deduction', 0),
            ('Gross Income', 0),
            ('Cost of Revenue', 0),
            ('Other Income', 0),
            ('Total Expenses', 10000),
            ('Expenses', 10000),
            ('Depreciation', 0),
            ('NET PROFIT', -10000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | -5750     |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      | 250       |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            | -10000    |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 86000     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 195000    |
        Cash out                                                                      | -109000   |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 80250     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 80250     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 45000),
            ('Cash in', 145000),
            ('Cash out', -100000),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', 35250),
            ('Net increase in cash and cash equivalents', 80250),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 80250),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 1200 for a one-year internet payment
        journal_items_11 = [{
            'account_id': self.default_account_prepayments.id,
            'debit': 1200,
            'credit': 0,
        },
        {
            'account_id': self.default_account_liquidity.id,
            'debit': 0,
            'credit': 1200,
        }]
        journal_entry_11 = self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_11)
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 89000       |
        Bank and Cash Accounts         | 79050       |
        Receivables                    | -250        |
        Current Assets                 | 9000        |
        Prepayments                    | 1200        |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        | 40000       |
        -------------------------------|-------------|
        ASSETS                         | 179000      |
        -------------------------------|-------------|
        Total Current Liabilities      | 34000       |
        Current Liabilities            | 30000       |
        Payables                       | 4000        |
        Non-current Liabilities        | 70000       |
        -------------------------------|-------------|
        LIABILITIES                    | 104000      |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          | -10000      |
        RETAINED EARNINGS              | 85000       |
        -------------------------------|-------------|
        EQUITY                         | 75000       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 89000),
            ('Bank and Cash Accounts', 79050),
            ('Receivables', -250),
            ('Current Assets', 9000),
            ('Prepayments', 1200),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 40000),
            ('ASSETS', 179000),
            ('Total Current Liabilities', 34000),
            ('Current Liabilities', 30000),
            ('Payables', 4000),
            ('Non-current Liabilities', 70000),
            ('LIABILITIES', 104000),
            ('CURRENT YEAR EARNINGS', -10000),
            ('RETAINED EARNINGS', 85000),
            ('EQUITY', 75000),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | -5750     |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      | 250       |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            | -10000    |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 84800     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 195000    |
        Cash out                                                                      | -110200   |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 79050     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 79050     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 43800),
            ('Cash in', 145000),
            ('Cash out', -101200),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', 35250),
            ('Net increase in cash and cash equivalents', 79050),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 79050),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 The cost of internet on a monthly basis is 120
        journal_items_12 = [{
            'account_id': self.default_account_expense.id,
            'debit': 120,
            'credit': 0,
        },
        {
            'account_id': self.default_account_prepayments.id,
            'debit': 0,
            'credit': 120,
        }]
        journal_entry_12 = self._init_journal_entry(None, datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_12)
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 88880       |
        Bank and Cash Accounts         | 79050       |
        Receivables                    | -250        |
        Current Assets                 | 9000        |
        Prepayments                    | 1080        |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        | 40000       |
        -------------------------------|-------------|
        ASSETS                         | 178880      |
        -------------------------------|-------------|
        Total Current Liabilities      | 34000       |
        Current Liabilities            | 30000       |
        Payables                       | 4000        |
        Non-current Liabilities        | 70000       |
        -------------------------------|-------------|
        LIABILITIES                    | 104000      |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          | -10120      |
        RETAINED EARNINGS              | 85000       |
        -------------------------------|-------------|
        EQUITY                         | 74880       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 88880),
            ('Bank and Cash Accounts', 79050),
            ('Receivables', -250),
            ('Current Assets', 9000),
            ('Prepayments', 1080),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 40000),
            ('ASSETS', 178880),
            ('Total Current Liabilities', 34000),
            ('Current Liabilities', 30000),
            ('Payables', 4000),
            ('Non-current Liabilities', 70000),
            ('LIABILITIES', 104000),
            ('CURRENT YEAR EARNINGS', -10120),
            ('RETAINED EARNINGS', 85000),
            ('EQUITY', 74880),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------------|
        |Expect value (Profit and Loss)|
        |------------------------------|
        Line items                     | 2021     |
        -------------------------------|----------|
        Total Income                   |          |
        -------------------------------|----------|
        Total Gross Profit             |          |
        Operating Income               |          |
        Financial Income               |          |
        Income Deduction               |          |
        Gross Income                   |          |
        Cost of Revenue                |          |
        Other Income                   |          |
        -------------------------------|----------|
        Total Expenses                 | 10120    |
        -------------------------------|----------|
        Expenses                       | 10120    |
        Depreciation                   |          |
        -------------------------------|----------|
        NET PROFIT                     | -10120   |
        -------------------------------|----------|
        """
        lines = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Income', 0),
            ('Total Gross Profit', 0),
            ('Operating Income', 0),
            ('Financial Income', 0),
            ('Income Deduction', 0),
            ('Gross Income', 0),
            ('Cost of Revenue', 0),
            ('Other Income', 0),
            ('Total Expenses', 10120),
            ('Expenses', 10120),
            ('Depreciation', 0),
            ('NET PROFIT', -10120),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | -5870     |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      | 250       |
        Cash received from operating activities                                       |           |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            | -10120    |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 84920     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 195120    |
        Cash out                                                                      | -110200   |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 79050     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 79050     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 43800),
            ('Cash in', 145000),
            ('Cash out', -101200),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', 35250),
            ('Net increase in cash and cash equivalents', 79050),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 79050),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 Uncollected sales (equipment) totaled 5000, with a record cost of equipment of 3000.
        journal_items_13 = [{
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
        journal_entry_13 = self._init_journal_entry(self.customer_a , datetime(2021, 1, 1, 12, 0), self.default_journal_sale, items=journal_items_13)
        """
        |----------------------------|
        |Expect value (Balance Sheet)|
        |----------------------------|
        Line items                     | As of today |
        -------------------------------|-------------|
        Total Current Assets           | 90880       |
        Bank and Cash Accounts         | 79050       |
        Receivables                    | 4750        |
        Current Assets                 | 6000        |
        Prepayments                    | 1080        |
        Plus Fixed Assets              | 50000       |
        Plus Non-current Assets        | 40000       |
        -------------------------------|-------------|
        ASSETS                         | 180880      |
        -------------------------------|-------------|
        Total Current Liabilities      | 34000       |
        Current Liabilities            | 30000       |
        Payables                       | 4000        |
        Non-current Liabilities        | 70000       |
        -------------------------------|-------------|
        LIABILITIES                    | 104000      |
        -------------------------------|-------------|
        CURRENT YEAR EARNINGS          | -8120       |
        RETAINED EARNINGS              | 85000       |
        -------------------------------|-------------|
        EQUITY                         | 76880       |
        -------------------------------|-------------|
        """
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2021, 8, 17, 12, 0), 'today')
        table_value = [
            ('Total Current Assets', 90880),
            ('Bank and Cash Accounts', 79050),
            ('Receivables', 4750),
            ('Current Assets', 6000),
            ('Prepayments', 1080),
            ('Plus Fixed Assets', 50000),
            ('Plus Non-current Assets', 40000),
            ('ASSETS', 180880),
            ('Total Current Liabilities', 34000),
            ('Current Liabilities', 30000),
            ('Payables', 4000),
            ('Non-current Liabilities', 70000),
            ('LIABILITIES', 104000),
            ('CURRENT YEAR EARNINGS', -8120),
            ('RETAINED EARNINGS', 85000),
            ('EQUITY', 76880),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------------|
        |Expect value (Profit and Loss)|
        |------------------------------|
        Line items                     | 2021     |
        -------------------------------|----------|
        Total Income                   | 2000     |
        -------------------------------|----------|
        Total Gross Profit             | 2000     |
        Operating Income               | 5000     |
        Financial Income               |          |
        Income Deduction               |          |
        Gross Income                   | 5000     |
        Cost of Revenue                | 3000     |
        Other Income                   |          |
        -------------------------------|----------|
        Total Expenses                 | 10120    |
        -------------------------------|----------|
        Expenses                       | 10120    |
        Depreciation                   |          |
        -------------------------------|----------|
        NET PROFIT                     | -8120    |
        -------------------------------|----------|
        """
        lines = self._get_lines_report(self.AccountProfitLossReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Income', 2000),
            ('Total Gross Profit', 2000),
            ('Operating Income', 5000),
            ('Financial Income', 0),
            ('Income Deduction', 0),
            ('Gross Income', 5000),
            ('Cost of Revenue', 3000),
            ('Other Income', 0),
            ('Total Expenses', 10120),
            ('Expenses', 10120),
            ('Depreciation', 0),
            ('NET PROFIT', -8120),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | -8870     |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      | -4750     |
        Cash received from operating activities                                       | 5000      |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            | -13120    |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 87920     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 198120    |
        Cash out                                                                      | -110200   |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 79050     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 79050     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 43800),
            ('Cash in', 145000),
            ('Cash out', -101200),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', 35250),
            ('Net increase in cash and cash equivalents', 79050),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 79050),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 Interest on the exchange rate 28
        journal_items_14 = [{
            'account_id': self.default_account_liquidity.id,
            'debit': 28,
            'credit': 0,
        },
        {
            'account_id': self.default_account_foreign.id,
            'debit': 0,
            'credit': 28,
        }]
        journal_entry_14 = self._init_journal_entry(None , datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_14)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | -8870     |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      | -4750     |
        Cash received from operating activities                                       | 5000      |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            | -13120    |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    | 28        |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 28        |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 87920     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 198120    |
        Cash out                                                                      | -110200   |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 79078     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 79078     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', 28),
            ('Cash in', 28),
            ('Cash out', 0),
            ('Total Cash flows from unclassified activities', 43800),
            ('Cash in', 145000),
            ('Cash out', -101200),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', 35250),
            ('Net increase in cash and cash equivalents', 79078),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 79078),
        ]
        self._check_report_value(lines, table_value)

        # 01/01/2021 Loss of exchange rate 39
        journal_items_15 = [{
            'account_id': self.default_account_foreign.id,
            'debit': 39,
            'credit': 0,
        },
        {
            'account_id': self.default_account_liquidity.id,
            'debit': 0,
            'credit': 39,
        }]
        journal_entry_15 = self._init_journal_entry(None , datetime(2021, 1, 1, 12, 0), self.default_journal_misc, items=journal_items_15)

        """
        |------------------------|
        |Expect value (Cash Flow)|
        |------------------------|
        Line Items                                                                    | 2021      |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from operating activities                                    | -8870     |
        ------------------------------------------------------------------------------|-----------|
        Advance Payments received from customers                                      | -4750     |
        Cash received from operating activities                                       | 5000      |
        Advance payments made to suppliers                                            | 4000      |
        Cash paid for operating activities                                            | -13120    |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from investing & extraordinary activities                    |           |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       |           |
        Cash out                                                                      |           |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from financing activities                                    | -11       |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 28        |
        Cash out                                                                      | -39       |
        ------------------------------------------------------------------------------|-----------|
        Total Cash flows from unclassified activities                                 | 87920     |
        ------------------------------------------------------------------------------|-----------|
        Cash in                                                                       | 198120    |
        Cash out                                                                      | -110200   |
        ------------------------------------------------------------------------------|-----------|
        Net increase in cash and cash equivalents                                     | 79039     |
        ------------------------------------------------------------------------------|-----------|
        Cash and cash equivalents, beginning of period                                |           |
        Cash and cash equivalents, closing balance                                    | 79039     |
        ------------------------------------------------------------------------------|-----------|
        """
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 8, 17, 12, 0), 'this_year')
        table_value = [
            ('Total Cash flows from operating activities', 0),
            ('Advance Payments received from customers', 0),
            ('Cash received from operating activities', 0),
            ('Advance payments made to suppliers', 0),
            ('Cash paid for operating activities', 0),
            ('Total Cash flows from investing & extraordinary activities', 0),
            ('Cash in', 0),
            ('Cash out', 0),
            ('Total Cash flows from financing activities', -11),
            ('Cash in', 28),
            ('Cash out', -39),
            ('Total Cash flows from unclassified activities', 43800),
            ('Cash in', 145000),
            ('Cash out', -101200),
            ('Minus previously recorded advance payments (already\n\t\t\t\tin the starting balance)\n\t\t\t', 35250),
            ('Net increase in cash and cash equivalents', 79039),
            ('Cash and cash equivalents, beginning of period', 0),
            ('Cash and cash equivalents, closing balance', 79039),
        ]
        self._check_report_value(lines, table_value)