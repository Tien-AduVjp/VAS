from datetime import datetime, date
from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class TrialBalance(Common):

    def setUp(self):
        super(TrialBalance, self).setUp()
        self.AccountTrialBalance = self.env['account.coa.report']

    def test_01_validate_trial_balance(self):
        # 12/08/2020 Capital contribution 100 cash
        journal_items_1 = [{
            'account_id': self.default_account_capital.id,
            'debit': 0,
            'credit': 100,
        },
        {
            'account_id': self.default_account_cash.id,
            'debit': 100,
            'credit': 0,
        }]
        journal_entry_1 = self._init_journal_entry(None , datetime(2020, 8, 12, 12, 0), self.default_journal_misc, items=journal_items_1)
        """
        |------------|
        |Expect value|
        |------------|

         Code   | Name           | Initial Balance |   Period Time   |      Total      |
                |                | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        --------|--------------- |--------|--------|--------|--------|--------|--------|
         101501 | Cash           | 100    |        |        |        | 100    |        |
         301000 | Capital        |        | 100    |        |        |        | 100    |
        --------|----------------|-----------------|--------|--------|--------|--------|
                | Total          | 100    | 100    |        |        | 100    | 100    |
        """
        lines = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Cash', 100, 0, 0, 0, 100, 0),
            ('Capital', 0, 100, 0, 0, 0, 100),
            ('Total', 100, 100, 0, 0, 100, 100),
        ]
        self._check_report_value(lines, table_value)

        # 12/08/2020 Capital contribution 700 bank
        journal_items_2 = [{
            'account_id': self.default_account_capital.id,
            'debit': 0,
            'credit': 700,
        },
        {
            'account_id': self.default_account_liquidity.id,
            'debit': 700,
            'credit': 0,
        }]
        journal_entry_2 = self._init_journal_entry(None , datetime(2020, 8, 12, 12, 0), self.default_journal_misc, items=journal_items_2)
        """
        |------------|
        |Expect value|
        |------------|

         Code   | Name           | Initial Balance |   Period Time   |      Total      |
                |                | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        --------|--------------- |--------|--------|--------|--------|--------|--------|
         101401 | Bank           | 700    |        |        |        | 700    |        |
         101501 | Cash           | 100    |        |        |        | 100    |        |
         301000 | Capital        |        | 800    |        |        |        | 800    |
        --------|----------------|-----------------|--------|--------|--------|--------|
                | Total          | 800    | 800    |        |        | 800    | 800    |
        """
        lines = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Bank', 700, 0, 0, 0, 700, 0),
            ('Cash', 100, 0, 0, 0, 100, 0),
            ('Capital', 0, 800, 0, 0, 0, 800),
            ('Total', 800, 800, 0, 0, 800, 800),
        ]
        self._check_report_value(lines, table_value)

        # 12/08/2020 Create vendor bill 500 for vendor a
        journal_items_3 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 500,
            'date_maturity': date(2020, 8, 12),
        },
        {
            'account_id': self.default_account_expense.id,
            'debit': 500,
            'credit': 0,
            'date_maturity': date(2020, 8, 12),
        }]
        journal_entry_3_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2020, 8, 12, 12, 0), self.default_journal_purchase, items=journal_items_3)
        """
        |------------|
        |Expect value|
        |------------|

         Code   | Name                          | Initial Balance |   Period Time   |      Total      |
                |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        --------|-------------------------------|--------|--------|--------|--------|--------|--------|
         101401 | Bank                          | 700    |        |        |        | 700    |        |
         101501 | Cash                          | 100    |        |        |        | 100    |        |
         211000 | Account Payable               |        | 500    |        |        |        | 500    |
         301000 | Capital                       |        | 800    |        |        |        | 800    |
         999999 | Undistributed Profits/Losses  | 500    |        |        |        | 500    |        |
        --------|-------------------------------|-----------------|--------|--------|--------|--------|
                | Total                         | 1300   | 1300   |        |        | 1300   | 1300   |
        """
        lines = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Bank', 700, 0, 0, 0, 700, 0),
            ('Cash', 100, 0, 0, 0, 100, 0),
            ('Account Payable', 0, 500, 0, 0, 0, 500),
            ('Capital', 0, 800, 0, 0, 0, 800),
            ('Undistributed Profits/Losses', 500, 0, 0, 0, 500, 0),
            ('Total', 1300, 1300, 0, 0, 1300, 1300),
        ]
        self._check_report_value(lines, table_value)

        # 12/08/2020 Create vendor bill 200 for vendor a
        journal_items_4 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 200,
            'date_maturity': date(2020, 8, 12),
        },
        {
            'account_id': self.default_account_stock.id,
            'debit': 200,
            'credit': 0,
            'date_maturity': date(2020, 8, 12),
        }]
        journal_entry_4_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2020, 8, 12, 12, 0), self.default_journal_purchase, items=journal_items_4)
        """
        |------------|
        |Expect value|
        |------------|

         Code   | Name                          | Initial Balance |   Period Time   |      Total      |
                |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        --------|-------------------------------|--------|--------|--------|--------|--------|--------|
         101401 | Bank                          | 700    |        |        |        | 700    |        |
         101501 | Cash                          | 100    |        |        |        | 100    |        |
         110200 | Stock Interim (Received)      | 200    |        |        |        | 200    |        |
         211000 | Account Payable               |        | 700    |        |        |        | 700    |
         301000 | Capital                       |        | 800    |        |        |        | 800    |
         999999 | Undistributed Profits/Losses  | 500    |        |        |        | 500    |        |
        --------|-------------------------------|-----------------|--------|--------|--------|--------|
                | Total                         | 1500   | 1500   |        |        | 1500   | 1500   |
        """
        lines = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Bank', 700, 0, 0, 0, 700, 0),
            ('Cash', 100, 0, 0, 0, 100, 0),
            ('Stock Interim (Received)', 200, 0, 0, 0, 200, 0),
            ('Account Payable', 0, 700, 0, 0, 0, 700),
            ('Capital', 0, 800, 0, 0, 0, 800),
            ('Undistributed Profits/Losses', 500, 0, 0, 0, 500, 0),
            ('Total', 1500, 1500, 0, 0, 1500, 1500),
        ]
        self._check_report_value(lines, table_value)

        # 12/08/2020 Create customer invoice 200 for customer a
        journal_items_5 = [{
            'account_id': self.default_account_revenue.id,
            'debit': 0,
            'credit': 200,
            'date_maturity': date(2020, 8, 12),
        },
        {
            'account_id': self.default_account_receivable.id,
            'debit': 200,
            'credit': 0,
            'date_maturity': date(2020, 8, 12),
        }]
        journal_entry_5_customer_a = self._init_journal_entry(self.customer_a, datetime(2020, 8, 12, 12, 0), self.default_journal_sale, items=journal_items_5)
        """
        |------------|
        |Expect value|
        |------------|

         Code   | Name                          | Initial Balance |   Period Time   |      Total      |
                |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        --------|-------------------------------|--------|--------|--------|--------|--------|--------|
         101401 | Bank                          | 700    |        |        |        | 700    |        |
         101501 | Cash                          | 100    |        |        |        | 100    |        |
         110200 | Stock Interim (Received)      | 200    |        |        |        | 200    |        |
         110200 | Account Receivable            | 200    |        |        |        | 200    |        |
         211000 | Account Payable               |        | 700    |        |        |        | 700    |
         301000 | Capital                       |        | 800    |        |        |        | 800    |
         999999 | Undistributed Profits/Losses  | 300    |        |        |        | 300    |        |
        --------|-------------------------------|-----------------|--------|--------|--------|--------|
                | Total                         | 1500   | 1500   |        |        | 1500   | 1500   |
        """
        lines = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Bank', 700, 0, 0, 0, 700, 0),
            ('Cash', 100, 0, 0, 0, 100, 0),
            ('Stock Interim (Received)', 200, 0, 0, 0, 200, 0),
            ('Account Receivable', 200, 0, 0, 0, 200, 0),
            ('Account Payable', 0, 700, 0, 0, 0, 700),
            ('Capital', 0, 800, 0, 0, 0, 800),
            ('Undistributed Profits/Losses', 300, 0, 0, 0, 300, 0),
            ('Total', 1500, 1500, 0, 0, 1500, 1500),
        ]
        self._check_report_value(lines, table_value)

        # 05/01/2021 Capital contribution 500 cash
        journal_items_6 = [{
            'account_id': self.default_account_capital.id,
            'debit': 0,
            'credit': 500,
        },
        {
            'account_id': self.default_account_cash.id,
            'debit': 500,
            'credit': 0,
        }]
        journal_entry_6 = self._init_journal_entry(None , datetime(2021, 1, 5, 12, 0), self.default_journal_misc, items=journal_items_6)
        """
        |------------|
        |Expect value|
        |------------|

         Code   | Name                          | Initial Balance |   Period Time   |      Total      |
                |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        --------|-------------------------------|--------|--------|--------|--------|--------|--------|
         101401 | Bank                          | 700    |        |        |        | 700    |        |
         101501 | Cash                          | 100    |        | 500    |        | 600    |        |
         110200 | Stock Interim (Received)      | 200    |        |        |        | 200    |        |
         110200 | Account Receivable            | 200    |        |        |        | 200    |        |
         211000 | Account Payable               |        | 700    |        |        |        | 700    |
         301000 | Capital                       |        | 800    |        | 500    |        | 1300   |
         999999 | Undistributed Profits/Losses  | 300    |        |        |        | 300    |        |
        --------|-------------------------------|-----------------|--------|--------|--------|--------|
                | Total                         | 1500   | 1500   | 500    | 500    | 2000   | 2000   |
        """
        lines = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Bank', 700, 0, 0, 0, 700, 0),
            ('Cash', 100, 0, 500, 0, 600, 0),
            ('Stock Interim (Received)', 200, 0, 0, 0, 200, 0),
            ('Account Receivable', 200, 0, 0, 0, 200, 0),
            ('Account Payable', 0, 700, 0, 0, 0, 700),
            ('Capital', 0, 800, 0, 500, 0, 1300),
            ('Undistributed Profits/Losses', 300, 0, 0, 0, 300, 0),
            ('Total', 1500, 1500, 500, 500, 2000, 2000),
        ]
        self._check_report_value(lines, table_value)

        # 10/02/2020 Create vendor bill 300 for vendor a
        journal_items_7 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 300,
            'date_maturity': date(2021, 2, 10),
        },
        {
            'account_id': self.default_account_stock.id,
            'debit': 300,
            'credit': 0,
            'date_maturity': date(2021, 2, 10),
        }]
        journal_entry_7_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 2, 10, 12, 0), self.default_journal_purchase, items=journal_items_7)
        """
        |------------|
        |Expect value|
        |------------|

         Code   | Name                          | Initial Balance |   Period Time   |      Total      |
                |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        --------|-------------------------------|--------|--------|--------|--------|--------|--------|
         101401 | Bank                          | 700    |        |        |        | 700    |        |
         101501 | Cash                          | 100    |        | 500    |        | 600    |        |
         110200 | Stock Interim (Received)      | 200    |        | 300    |        | 500    |        |
         110200 | Account Receivable            | 200    |        |        |        | 200    |        |
         211000 | Account Payable               |        | 700    |        | 300    |        | 1000   |
         301000 | Capital                       |        | 800    |        | 500    |        | 1300   |
         999999 | Undistributed Profits/Losses  | 300    |        |        |        | 300    |        |
        --------|-------------------------------|-----------------|--------|--------|--------|--------|
                | Total                         | 1500   | 1500   | 800    | 800    | 2300   | 2300   |
        """
        lines = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Bank', 700, 0, 0, 0, 700, 0),
            ('Cash', 100, 0, 500, 0, 600, 0),
            ('Stock Interim (Received)', 200, 0, 300, 0, 500, 0),
            ('Account Receivable', 200, 0, 0, 0, 200, 0),
            ('Account Payable', 0, 700, 0, 300, 0, 1000),
            ('Capital', 0, 800, 0, 500, 0, 1300),
            ('Undistributed Profits/Losses', 300, 0, 0, 0, 300, 0),
            ('Total', 1500, 1500, 800, 800, 2300, 2300),
        ]
        self._check_report_value(lines, table_value)

        # 13/08/2021 Change accounting period 01/02/2021 - 28/02/2021
        """
        |------------|
        |Expect value|
        |------------|

         Code   | Name                          | Initial Balance |   Period Time   |      Total      |
                |                               | Debit  | Credit | Debit  | Credit | Debit  | Credit |
        --------|-------------------------------|--------|--------|--------|--------|--------|--------|
         101401 | Bank                          | 700    |        |        |        | 700    |        |
         101501 | Cash                          | 600    |        |        |        | 600    |        |
         110200 | Stock Interim (Received)      | 200    |        | 300    |        | 500    |        |
         110200 | Account Receivable            | 200    |        |        |        | 200    |        |
         211000 | Account Payable               |        | 700    |        | 300    |        | 1000   |
         301000 | Capital                       |        | 1300   |        |        |        | 1300   |
         999999 | Undistributed Profits/Losses  | 300    |        |        |        | 300    |        |
        --------|-------------------------------|-----------------|--------|--------|--------|--------|
                | Total                         | 2000   | 2000   | 300    | 300    | 2300   | 2300   |
        """
        lines = self._get_lines_report(self.AccountTrialBalance, datetime(2021, 8, 13, 12, 0), 'custom', date(2021, 2, 1), date(2021, 2, 28))
        table_value = [
            ('Bank', 700, 0, 0, 0, 700, 0),
            ('Cash', 600, 0, 0, 0, 600, 0),
            ('Stock Interim (Received)', 200, 0, 300, 0, 500, 0),
            ('Account Receivable', 200, 0, 0, 0, 200, 0),
            ('Account Payable', 0, 700, 0, 300, 0, 1000),
            ('Capital', 0, 1300, 0, 0, 0, 1300),
            ('Undistributed Profits/Losses', 300, 0, 0, 0, 300, 0),
            ('Total', 2000, 2000, 300, 300, 2300, 2300),
        ]
        self._check_report_value(lines, table_value)
