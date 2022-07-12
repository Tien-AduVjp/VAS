from datetime import datetime, date
from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class GeneralLedger(Common):

    def setUp(self):
        super(GeneralLedger, self).setUp()
        self.AccountGeneralLedger = self.env['account.general.ledger']

    def test_01_validate_general_ledger(self):
        # 13/08/2021 Create vendor bill 10 for vendor a
        journal_items_1 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 10,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_expense.id,
            'debit': 10,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_1_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0), self.default_journal_purchase, items=journal_items_1)
        """
        |------------|
        |Expect value|
        |------------|

                                    |  |  |  |  | Debit | Credit | Balance |
        ----------------------------|--|--|--|--|-------|--------|---------|
        211000 Account Payable      |  |  |  |  | 0     | 10     | -10     |
        600000 Expenses             |  |  |  |  | 10    | 0      | 10      |
        ----------------------------|--|--|--|--|-------|--------|---------|
        """
        lines = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        table_value = [
            ('211000 Account Payable', 0, 0, 0, 0, 0, 10, -10),
            ('600000 Expenses'   , 0, 0, 0, 0, 10, 0, 10),
        ]
        self._check_report_value(lines, table_value)

        # 13/08/2021 Create vendor payment 10 for vendor a
        journal_items_2 = [{
            'account_id': self.default_account_cash.id,
            'debit': 0,
            'credit': 10,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_payable.id,
            'debit': 10,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_2_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0), self.default_journal_bank, items=journal_items_2)
        """
        |------------|
        |Expect value|
        |------------|

                                    |  |  |  |  | Debit | Credit | Balance |
        ----------------------------|--|--|--|--|-------|--------|---------|
        101501 Cash                 |  |  |  |  | 0     | 10     | -10     |
        211000 Account Payable      |  |  |  |  | 10    | 10     | 0       |
        600000 Expenses             |  |  |  |  | 10    | 0      | 10      |
        ----------------------------|--|--|--|--|-------|--------|---------|
        """
        lines = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        table_value = [
            ('101501 Cash'   , 0, 0, 0, 0, 0, 10, -10),
            ('211000 Account Payable', 0, 0, 0, 0, 10, 10, 0),
            ('600000 Expenses'   , 0, 0, 0, 0, 10, 0, 10),
        ]
        self._check_report_value(lines, table_value)

        # Change the value of journal entry 1 from 10 to 15
        journal_entry_1_vendor_a.button_draft()
        journal_items_new_1 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 15,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_expense.id,
            'debit': 15,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_new_1_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0),
                                                                self.default_journal_purchase, items=journal_items_new_1)
        """
        |------------|
        |Expect value|
        |------------|

                                    |  |  |  |  | Debit | Credit | Balance |
        ----------------------------|--|--|--|--|-------|--------|---------|
        101501 Cash                 |  |  |  |  | 0     | 10     | -10     |
        211000 Account Payable      |  |  |  |  | 10    | 15     | -5      |
        600000 Expenses             |  |  |  |  | 15    | 0      | 15      |
        ----------------------------|--|--|--|--|-------|--------|---------|
        """
        lines = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        table_value = [
            ('101501 Cash'   , 0, 0, 0, 0, 0, 10, -10),
            ('211000 Account Payable', 0, 0, 0, 0, 10, 15, -5),
            ('600000 Expenses'   , 0, 0, 0, 0, 15, 0, 15),
        ]
        self._check_report_value(lines, table_value)

        # Change the value of journal entry 2 from 10 to 15
        journal_entry_2_vendor_a.button_draft()
        journal_items_new_2 = [{
            'account_id': self.default_account_cash.id,
            'debit': 0,
            'credit': 15,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_payable.id,
            'debit': 15,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_new_2_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0),
                                                            self.default_journal_bank, items=journal_items_new_2)
        """
        |------------|
        |Expect value|
        |------------|

                                    |  |  |  |  | Debit | Credit | Balance |
        ----------------------------|--|--|--|--|-------|--------|---------|
        101501 Cash                 |  |  |  |  | 0     | 15     | -15     |
        211000 Account Payable      |  |  |  |  | 15    | 15     | 0       |
        600000 Expenses             |  |  |  |  | 15    | 0      | 15      |
        ----------------------------|--|--|--|--|-------|--------|---------|
        """
        lines = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        table_value = [
            ('101501 Cash'   , 0, 0, 0, 0, 0, 15, -15),
            ('211000 Account Payable', 0, 0, 0, 0, 15, 15, 0),
            ('600000 Expenses'   , 0, 0, 0, 0, 15, 0, 15),
        ]
        self._check_report_value(lines, table_value)

    def test_02_validate_general_ledger(self):
        # 13/08/2021 Create vendor bill 10 for vendor a
        journal_items_1 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 10,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id
        },
        {
            'account_id': self.default_account_stock.id,
            'debit': 10,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id
        }]
        journal_entry_1_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0), self.default_journal_purchase, items=journal_items_1)
        """
        |------------|
        |Expect value|
        |------------|

                                            |  |  |  |  | Debit | Credit | Balance |
        ------------------------------------|--|--|--|--|-------|--------|---------|
        110200 Stock Interim (Received)     |  |  |  |  | 10    | 0      | 10      |
        211000 Account Payable              |  |  |  |  | 0     | 10     | -10     |
        ------------------------------------|--|--|--|--|-------|--------|---------|
        """
        lines = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        table_value = [
            ('110200 Stock Interim (Received)', 0, 0, 0, 0, 10, 0, 10),
            ('211000 Account Payable', 0, 0, 0, 0, 0, 10, -10),
        ]
        self._check_report_value(lines, table_value)

        # 13/08/2021 Create vendor payment 10 for vendor a
        journal_items_2 = [{
            'account_id': self.default_account_cash.id,
            'debit': 0,
            'credit': 10,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id
        },
        {
            'account_id': self.default_account_payable.id,
            'debit': 10,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id
        }]
        journal_entry_2_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0), self.default_journal_bank, items=journal_items_2)
        """
        |------------|
        |Expect value|
        |------------|

                                            |  |  |  |  | Debit | Credit | Balance |
        ------------------------------------|--|--|--|--|-------|--------|---------|
        101501 Cash                         |  |  |  |  | 0     | 10     | -10     |
        110200 Stock Interim (Received)     |  |  |  |  | 10    | 0      | 10      |
        211000 Account Payable              |  |  |  |  | 10    | 10     | 0       |
        ------------------------------------|--|--|--|--|-------|--------|---------|
        """
        lines = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        table_value = [
            ('101501 Cash', 0, 0, 0, 0, 0, 10, -10),
            ('110200 Stock Interim (Received)', 0, 0, 0, 0, 10, 0, 10),
            ('211000 Account Payable', 0, 0, 0, 0, 10, 10, 0),
        ]
        self._check_report_value(lines, table_value)

        # Change the price of journal entry 1 from 10 to 15
        journal_entry_1_vendor_a.button_draft()
        journal_items_new_1 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 15,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id
        },
        {
            'account_id': self.default_account_stock.id,
            'debit': 15,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id
        }]
        journal_entry_new_1_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0),
                                                                self.default_journal_purchase, items=journal_items_new_1)
        """
        |------------|
        |Expect value|
        |------------|

                                            |  |  |  |  | Debit | Credit | Balance |
        ------------------------------------|--|--|--|--|-------|--------|---------|
        101501 Cash                         |  |  |  |  | 0     | 10     | -10     |
        110200 Stock Interim (Received)     |  |  |  |  | 15    | 0      | 15      |
        211000 Account Payable              |  |  |  |  | 10    | 15     | -5      |
        ------------------------------------|--|--|--|--|-------|--------|---------|
        """
        lines = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        table_value = [
            ('101501 Cash', 0, 0, 0, 0, 0, 10, -10),
            ('110200 Stock Interim (Received)', 0, 0, 0, 0, 15, 0, 15),
            ('211000 Account Payable', 0, 0, 0, 0, 10, 15, -5),
        ]
        self._check_report_value(lines, table_value)

        # Change the price of journal entry 2 from 10 to 15
        journal_entry_2_vendor_a.button_draft()
        journal_items_new_2 = [{
            'account_id': self.default_account_cash.id,
            'debit': 0,
            'credit': 15,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id
        },
        {
            'account_id': self.default_account_payable.id,
            'debit': 15,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id
        }]
        journal_entry_new_2_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0),
                                                            self.default_journal_bank, items=journal_items_new_2)
        """
        |------------|
        |Expect value|
        |------------|

                                            |  |  |  |  | Debit | Credit | Balance |
        ------------------------------------|--|--|--|--|-------|--------|---------|
        101501 Cash                         |  |  |  |  | 0     | 15     | -15     |
        110200 Stock Interim (Received)     |  |  |  |  | 15    | 0      | 15      |
        211000 Account Payable              |  |  |  |  | 15    | 15     | 0       |
        ------------------------------------|--|--|--|--|-------|--------|---------|
        """
        lines = self._get_lines_report(self.AccountGeneralLedger, datetime(2021, 8, 13, 12, 0), 'this_month')
        table_value = [
            ('101501 Cash', 0, 0, 0, 0, 0, 15, -15),
            ('110200 Stock Interim (Received)', 0, 0, 0, 0, 15, 0, 15),
            ('211000 Account Payable', 0, 0, 0, 0, 15, 15, 0),
        ]
        self._check_report_value(lines, table_value)
