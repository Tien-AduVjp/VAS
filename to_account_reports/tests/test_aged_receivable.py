from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class AgedReceivable(Common):

    def setUp(self): 
        super(AgedReceivable, self).setUp()
        self.AccountAgedReceivable = self.env['account.aged.receivable']

    def test_01_validate_aged_receivable(self):
        # 13/08/2021 Create customer invoice 10 for customer a
        journal_items_1 = [{
            'account_id': self.default_account_revenue.id,
            'debit': 0,
            'credit': 10,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.customer_a.id
        },
        {
            'account_id': self.default_account_receivable.id,
            'debit': 10,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.customer_a.id
        }]
        journal_entry_1_customer_a = self._init_journal_entry(self.customer_a, datetime(2021, 8, 13, 12, 0), self.default_journal_sale, items=journal_items_1)
        """
        |------------|
        |Expect value|
        |------------|

                        | Not due on 08/13/2021     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Customer A      | 10                        | 0      | 0       | 0       | 0        | 0     | 10    |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Total           | 10                        | 0      | 0       | 0       | 0        | 0     | 10    |
        """
        lines = self._get_lines_report(self.AccountAgedReceivable, datetime(2021, 8, 13, 12, 0))
        table_value = [
            ('Customer A', 10, 0, 0, 0, 0, 0, 10),
            ('Total'   , 10, 0, 0, 0, 0, 0, 10),
        ]
        self._check_report_value(lines, table_value)
        
        """
        |------------|
        |Expect value|
        |------------|

                        | Not due on 08/30/2021     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Customer A      | 0                         | 10     | 0       | 0       | 0        | 0     | 10    |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Total           | 0                         | 10     | 0       | 0       | 0        | 0     | 10    |
        """
        lines = self._get_lines_report(self.AccountAgedReceivable, datetime(2021, 8, 30, 12, 0), 'custom')
        table_value = [
            ('Customer A', 0, 10, 0, 0, 0, 0, 10),
            ('Total'   , 0, 10, 0, 0, 0, 0, 10),
        ]
        self._check_report_value(lines, table_value)
        
        # Create customer payment 5 for customer a
        journal_items_2 = [{
            'account_id': self.default_account_receivable.id,
            'debit': 0,
            'credit': 5,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.customer_a.id
        },
        {
            'account_id': self.default_account_liquidity.id,
            'debit': 5,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.customer_a.id
        }]
        journal_entry_2_customer_a = self._init_journal_entry(self.customer_a, datetime(2021, 8, 13, 12, 0), self.default_journal_bank, items=journal_items_2)
        """
        |------------|
        |Expect value|
        |------------|

                        | Not due on 08/13/2021     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Customer A      | 5                         | 0      | 0       | 0       | 0        | 0     | 5     |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Total           | 5                         | 0      | 0       | 0       | 0        | 0     | 5     |
        """
        lines = self._get_lines_report(self.AccountAgedReceivable, datetime(2021, 8, 13, 12, 0))
        table_value = [
            ('Customer A', 5, 0, 0, 0, 0, 0, 5),
            ('Total'   , 5, 0, 0, 0, 0, 0, 5),
        ]
        self._check_report_value(lines, table_value)

    def test_02_validate_aged_receivable(self):
        # Create customer invoice 20 for customer a
        # Payment terms: Now, pay 10. After 45 days, pay 10
        journal_items_1 = [{
            'account_id': self.default_account_revenue.id,
            'debit': 0,
            'credit': 20,
            'partner_id': self.customer_a.id
        },
        {
            'account_id': self.default_account_receivable.id,
            'debit': 10,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
            'partner_id': self.customer_a.id
        },
        {
            'account_id': self.default_account_receivable.id,
            'debit': 10,
            'credit': 0,
            'date_maturity': date(2021, 8, 13) + relativedelta(days=45),
            'partner_id': self.customer_a.id
        }]
        journal_entry_1_customer_a = self._init_journal_entry(self.customer_a, datetime(2021, 8, 13, 12, 0), self.default_journal_sale, items=journal_items_1)
        """
        |------------|
        |Expect value|
        |------------|

                        | Not due on 08/13/2021     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Customer A      | 20                        | 0      | 0       | 0       | 0        | 0     | 20    |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Total           | 20                        | 0      | 0       | 0       | 0        | 0     | 20    |
        """
        lines = self._get_lines_report(self.AccountAgedReceivable, datetime(2021, 8, 13, 12, 0))
        table_value = [
            ('Customer A', 20, 0, 0, 0, 0, 0, 20),
            ('Total'   , 20, 0, 0, 0, 0, 0, 20),
        ]
        self._check_report_value(lines, table_value)
        
        """
        |------------|
        |Expect value|
        |------------|

                        | Not due on 08/13/2021     | 0 - 30 | 30 - 60 | 60 - 90 | 90 - 120 | Older | Total |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Customer A      | 10                        | 10     | 0       | 0       | 0        | 0     | 20    |
        ----------------|---------------------------|--------|---------|---------|----------|-------|-------|
        Total           | 10                        | 10     | 0       | 0       | 0        | 0     | 20    |
        """
        lines = self._get_lines_report(self.AccountAgedReceivable, datetime(2021, 8, 30, 12, 0), 'custom')
        table_value = [
            ('Customer A', 10, 10, 0, 0, 0, 0, 20),
            ('Total'   , 10, 10, 0, 0, 0, 0, 20),
        ]
        self._check_report_value(lines, table_value)
