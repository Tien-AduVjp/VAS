from datetime import datetime, date
from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class PartnerLedger(Common):

    def setUp(self):
        super(PartnerLedger, self).setUp()
        self.AccountPartnerLedger = self.env['account.partner.ledger']

    def test_01_validate_partner_ledger(self):
        # 11/08/2021 Create vendor bill 10 for vendor a
        journal_items_1 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 10,
            'date_maturity': date(2021, 8, 11),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_expense.id,
            'debit': 10,
            'credit': 0,
            'date_maturity': date(2021, 8, 11),
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_1_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 11, 12, 0), self.default_journal_purchase, items=journal_items_1)
        """
        |------------|
        |Expect value|
        |------------|

                        |  |  |  |  |  | Initial Debit | Initial Credit| Debit | Credit | End Debit | End Credit |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Vendor A        |  |  |  |  |  | 0             | 0             | 0     | 10     | 0         | 10         |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Total           |  |  |  |  |  | 0             | 0             | 0     | 10     | 0         | 10         |
        """
        lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 11, 12, 0), 'this_year')
        table_value = [
            ('Vendor A', 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 10),
            ('Total'   , 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 10),
        ]
        self._check_report_value(lines, table_value)

        # 12/08/2021 Create vendor bill 5 for vendor a
        journal_items_2 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 5,
            'date_maturity': date(2021, 8, 12),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_expense.id,
            'debit': 5,
            'credit': 0,
            'date_maturity': date(2021, 8, 12),
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_2_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 12, 12, 0), self.default_journal_purchase, items=journal_items_2)
        """
        |------------|
        |Expect value|
        |------------|

                        |  |  |  |  |  | Initial Debit | Initial Credit| Debit | Credit | End Debit | End Credit |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Vendor A        |  |  |  |  |  | 0             | 10            | 0     | 5      | 0         | 15         |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Total           |  |  |  |  |  | 0             | 10            | 0     | 5      | 0         | 15         |
        """
        lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 12, 12, 0), 'custom', date(2021, 8, 12), date(2021, 12, 31))
        table_value = [
            ('Vendor A', 0, 0, 0, 0, 0, 0, 10, 0, 5, 0, 15),
            ('Total'   , 0, 0, 0, 0, 0, 0, 10, 0, 5, 0, 15),
        ]
        self._check_report_value(lines, table_value)

        # 13/08/2021 Create vendor payment 5 for vendor a
        journal_items_3 = [{
            'account_id': self.default_account_cash.id,
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
        journal_entry_3_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0), self.default_journal_cash, items=journal_items_3)
        """
        |------------|
        |Expect value|
        |------------|

                        |  |  |  |  |  | Initial Debit | Initial Credit| Debit | Credit | End Debit | End Credit |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Vendor A        |  |  |  |  |  | 0             | 15            | 5     | 0      | 0         | 10         |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Total           |  |  |  |  |  | 0             | 15            | 5     | 0      | 0         | 10         |
        """
        lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 13, 12, 0), 'custom', date(2021, 8, 13), date(2021, 12, 31))
        table_value = [
            ('Vendor A', 0, 0, 0, 0, 0, 0, 15, 5, 0, 0, 10),
            ('Total'   , 0, 0, 0, 0, 0, 0, 15, 5, 0, 0, 10),
        ]
        self._check_report_value(lines, table_value)

        # 14/08/2021 Create vendor payment 10 for vendor a
        journal_items_4 = [{
            'account_id': self.default_account_cash.id,
            'debit': 0,
            'credit': 10,
            'date_maturity': date(2021, 8, 14),
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_payable.id,
            'debit': 10,
            'credit': 0,
            'date_maturity': date(2021, 8, 14),
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_4_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 14, 12, 0), self.default_journal_cash, items=journal_items_4)
        """
        |------------|
        |Expect value|
        |------------|

                        |  |  |  |  |  | Initial Debit | Initial Credit| Debit | Credit | End Debit | End Credit |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Vendor A        |  |  |  |  |  | 5             | 15            | 10    | 0      | 0         | 0          |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Total           |  |  |  |  |  | 5             | 15            | 10    | 0      | 0         | 0          |
        """
        lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 14, 12, 0), 'custom', date(2021, 8, 14), date(2021, 12, 31))
        table_value = [
            ('Vendor A', 0, 0, 0, 0, 0, 5, 15, 10, 0, 0, 0),
            ('Total'   , 0, 0, 0, 0, 0, 5, 15, 10, 0, 0, 0),
        ]
        self._check_report_value(lines, table_value)

    def test_02_validate_partner_ledger(self):
        # 11/08/2021 Create customer invoice 10 for customer a
        journal_items_1 = [{
            'account_id': self.default_account_revenue.id,
            'debit': 0,
            'credit': 10,
            'date_maturity': date(2021, 8, 11),
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_receivable.id,
            'debit': 10,
            'credit': 0,
            'date_maturity': date(2021, 8, 11),
            'partner_id': self.customer_a.id,
        }]
        journal_entry_1_customer_a = self._init_journal_entry(self.customer_a, datetime(2021, 8, 11, 12, 0), self.default_journal_sale, items=journal_items_1)
        """
        |------------|
        |Expect value|
        |------------|

                        |  |  |  |  |  | Initial Debit | Initial Credit| Debit | Credit | End Debit | End Credit |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Vendor A        |  |  |  |  |  | 0             | 0             | 10    | 0      | 10        | 0          |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Total           |  |  |  |  |  | 0             | 0             | 10    | 0      | 10        | 0          |
        """
        lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 11, 12, 0), 'this_year')
        table_value = [
            ('Customer A', 0, 0, 0, 0, 0, 0, 0, 10, 0, 10, 0),
            ('Total'   , 0, 0, 0, 0, 0, 0, 0, 10, 0, 10, 0),
        ]
        self._check_report_value(lines, table_value)

        # 12/08/2021 Create customer invoice 5 for customer a
        journal_items_2 = [{
            'account_id': self.default_account_revenue.id,
            'debit': 0,
            'credit': 5,
            'date_maturity': date(2021, 8, 12),
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_receivable.id,
            'debit': 5,
            'credit': 0,
            'date_maturity': date(2021, 8, 12),
            'partner_id': self.customer_a.id,
        }]
        journal_entry_2_customer_a = self._init_journal_entry(self.customer_a, datetime(2021, 8, 12, 12, 0), self.default_journal_sale, items=journal_items_2)
        """
        |------------|
        |Expect value|
        |------------|

                        |  |  |  |  |  | Initial Debit | Initial Credit| Debit | Credit | End Debit | End Credit |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Vendor A        |  |  |  |  |  | 10            | 0             | 0     | 5      | 15        | 0          |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Total           |  |  |  |  |  | 10            | 0             | 0     | 5      | 15        | 0          |
        """
        lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 12, 12, 0), 'custom', date(2021, 8, 12), date(2021, 12, 31))
        table_value = [
            ('Customer A', 0, 0, 0, 0, 0, 10, 0, 5, 0, 15, 0),
            ('Total'   , 0, 0, 0, 0, 0, 10, 0, 5, 0, 15, 0),
        ]
        self._check_report_value(lines, table_value)

        # 13/08/2021 Create customer payment 5 for customer a
        journal_items_3 = [{
            'account_id': self.default_account_receivable.id,
            'debit': 0,
            'credit': 5,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_cash.id,
            'debit': 5,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.customer_a.id,
        }]
        journal_entry_3_customer_a = self._init_journal_entry(self.customer_a, datetime(2021, 8, 13, 12, 0), self.default_journal_cash, items=journal_items_3)
        """
        |------------|
        |Expect value|
        |------------|

                        |  |  |  |  |  | Initial Debit | Initial Credit| Debit | Credit | End Debit | End Credit |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Vendor A        |  |  |  |  |  | 15            | 0             | 0     | 5      | 10        | 0          |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Total           |  |  |  |  |  | 15            | 0             | 0     | 5      | 10        | 0          |
        """
        lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 13, 12, 0), 'custom', date(2021, 8, 13), date(2021, 12, 31))
        table_value = [
            ('Customer A', 0, 0, 0, 0, 0, 15, 0, 0, 5, 10, 0),
            ('Total'   , 0, 0, 0, 0, 0, 15, 0, 0, 5, 10, 0),
        ]
        self._check_report_value(lines, table_value)

        # 14/08/2021 Create customer payment 10 for customer a
        journal_items_4 = [{
            'account_id': self.default_account_receivable.id,
            'debit': 0,
            'credit': 10,
            'date_maturity': date(2021, 8, 14),
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_cash.id,
            'debit': 10,
            'credit': 0,
            'date_maturity': date(2021, 8, 14),
            'partner_id': self.customer_a.id,
        }]
        journal_entry_4_customer_a = self._init_journal_entry(self.customer_a, datetime(2021, 8, 14, 12, 0), self.default_journal_cash, items=journal_items_4)
        """
        |------------|
        |Expect value|
        |------------|

                        |  |  |  |  |  | Initial Debit | Initial Credit| Debit | Credit | End Debit | End Credit |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Vendor A        |  |  |  |  |  | 15            | 5             | 0     | 10     | 0         | 0          |
        ----------------|--|--|--|--|--|---------------|---------------|-------|--------|-----------|------------|
        Total           |  |  |  |  |  | 15            | 5             | 0     | 10     | 0         | 0          |
        """
        lines = self._get_lines_report(self.AccountPartnerLedger, datetime(2021, 8, 14, 12, 0), 'custom', date(2021, 8, 14), date(2021, 12, 31))
        table_value = [
            ('Customer A', 0, 0, 0, 0, 0, 15, 5, 0, 10, 0, 0),
            ('Total'   , 0, 0, 0, 0, 0, 15, 5, 0, 10, 0, 0),
        ]
        self._check_report_value(lines, table_value)
