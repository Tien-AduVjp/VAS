from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class AgedPayable(Common):

    def setUp(self):
        super(AgedPayable, self).setUp()
        self.AccountAgedPayable = self.env['account.aged.payable']

    def test_01_validate_aged_payable(self):
        # 13/08/2021: Create vendor bill 10 for vendor a
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

                        | Not due on 08/13/2021     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Vendor A        | 10                        | 0      | 0       | 0       | 0        | 0     | 10    |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Total           | 10                        | 0      | 0       | 0       | 0        | 0     | 10    |
        """
        lines = self._get_lines_report(self.AccountAgedPayable, datetime(2021, 8, 13, 12, 0))
        table_value = [
            ('Vendor A', 10, 0, 0, 0, 0, 0, 10),
            ('Total'   , 10, 0, 0, 0, 0, 0, 10),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------|
        |Expect value|
        |------------|

                        | Not due on 08/30/2021     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Vendor A        | 0                         | 10     | 0       | 0       | 0        | 0     | 10    |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Total           | 0                         | 10     | 0       | 0       | 0        | 0     | 10    |
        """
        lines = self._get_lines_report(self.AccountAgedPayable, datetime(2021, 8, 30, 12, 0), 'custom')
        table_value = [
            ('Vendor A', 0, 10, 0, 0, 0, 0, 10),
            ('Total'   , 0, 10, 0, 0, 0, 0, 10),
        ]
        self._check_report_value(lines, table_value)

        # 13/08/2021 Create vendor payment 5 for vendor a
        journal_items_2 = [{
            'account_id': self.default_account_liquidity.id,
            'debit': 0,
            'credit': 5,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_payable.id,
            'debit': 5,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_2_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0), self.default_journal_bank, items=journal_items_2)
        """
        |------------|
        |Expect value|
        |------------|

                        | Not due on 08/13/2021     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Vendor A        | 5                         | 0      | 0       | 0       | 0        | 0     | 5     |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Total           | 5                         | 0      | 0       | 0       | 0        | 0     | 5     |
        """
        lines = self._get_lines_report(self.AccountAgedPayable, datetime(2021, 8, 13, 12, 0))
        table_value = [
            ('Vendor A', 5, 0, 0, 0, 0, 0, 5),
            ('Total'   , 5, 0, 0, 0, 0, 0, 5),
        ]
        self._check_report_value(lines, table_value)

    def test_02_validate_aged_payable(self):
        # 13/08/2021 Create vendor bill 20 for vendor a
        # Payment terms: Now, pay 10. After 45 days, pay 10
        journal_items_1 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 10,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 10,
            'date_maturity': date(2021, 8, 13) + relativedelta(days=45),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_expense.id,
            'debit': 20,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_1_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0), self.default_journal_purchase, items=journal_items_1)
        """
        |------------|
        |Expect value|
        |------------|

                        | Not due on 08/13/2021     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Vendor A        | 20                        | 0      | 0       | 0       | 0        | 0     | 20    |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Total           | 20                        | 0      | 0       | 0       | 0        | 0     | 20    |
        """
        lines = self._get_lines_report(self.AccountAgedPayable, datetime(2021, 8, 13, 12, 0))
        table_value = [
            ('Vendor A', 20, 0, 0, 0, 0, 0, 20),
            ('Total'   , 20, 0, 0, 0, 0, 0, 20),
        ]
        self._check_report_value(lines, table_value)

        """
        |------------|
        |Expect value|
        |------------|

                        | Not due on 08/30/2021     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Vendor A        | 10                        | 10     | 0       | 0       | 0        | 0     | 20    |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Total           | 10                        | 10     | 0       | 0       | 0        | 0     | 20    |
        """
        lines = self._get_lines_report(self.AccountAgedPayable, datetime(2021, 8, 30, 12, 0), 'custom')
        table_value = [
            ('Vendor A', 10, 10, 0, 0, 0, 0, 20),
            ('Total'   , 10, 10, 0, 0, 0, 0, 20),
        ]
        self._check_report_value(lines, table_value)
