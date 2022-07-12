from datetime import datetime, date
from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class TaxReport(Common):

    def setUp(self): 
        super(TaxReport, self).setUp()
        self.AccountTaxReport = self.env['account.generic.tax.report']

    def test_01_validate_tax_report(self):
        # 13/08/2021 Create vendor bill 100 for vendor a, tax 10%
        journal_items_1 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 110,
            'date_maturity': date(2021, 8, 13),
        },
        {
            'account_id': self.default_account_expense.id,
            'debit': 100,
            'credit': 0,
            'tax_ids': [(6, 0, self.tax_price_purchase_10.ids)]
        },
        {
            'account_id': self.default_account_tax_purchase.id,
            'debit': 10,
            'credit': 0,
            'tax_repartition_line_id': self.tax_repartition_line_purchase_10.id,
        }]
        journal_entry_1_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0), self.default_journal_purchase, items=journal_items_1)
        """
        |------------|
        |Expect value|
        |------------|

                                    | Net | Tax |
        ----------------------------|-----|-----|
        Sale                        | 0   | 0   |
        ----------------------------|-----|-----|
        Purchase                    | 0   | 0   |
            10% purchase (10.0)     | 100 | 10  |
        ----------------------------|-----|-----|
        """
        lines = self._get_lines_report(self.AccountTaxReport, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Sale', 0, 0),
            ('Purchase', 0, 0),
            ('10% purchase (10.0)', 100, 10),
        ]
        self._check_report_value(lines, table_value)

        # Change the main value form 100 to 150
        journal_entry_1_vendor_a.button_draft()
        journal_items_new_1 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 165,
            'date_maturity': date(2021, 8, 13),
        },
        {
            'account_id': self.default_account_expense.id,
            'debit': 150,
            'credit': 0,
            'tax_ids': [(6, 0, self.tax_price_purchase_10.ids)]
        },
        {
            'account_id': self.default_account_tax_purchase.id,
            'debit': 15,
            'credit': 0,
            'tax_repartition_line_id': self.tax_repartition_line_purchase_10.id,
        }]
        journal_entry_new_1_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0),
                                                            self.default_journal_purchase, items=journal_items_new_1)
        """
        |------------|
        |Expect value|
        |------------|

                                    | Net | Tax |
        ----------------------------|-----|-----|
        Sale                        | 0   | 0   |
        ----------------------------|-----|-----|
        Purchase                    | 0   | 0   |
            10% purchase (10.0)     | 150 | 15  |
        ----------------------------|-----|-----|
        """
        lines = self._get_lines_report(self.AccountTaxReport, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Sale', 0, 0),
            ('Purchase', 0, 0),
            ('10% purchase (10.0)', 150, 15),
        ]
        self._check_report_value(lines, table_value)

        # 13/08/2021 Create vendor bill 50 for vendor a, tax 5%
        journal_items_2 = [{
            'account_id': self.default_account_payable.id,
            'debit': 0,
            'credit': 52.5,
            'date_maturity': date(2021, 8, 13),
        },
        {
            'account_id': self.default_account_expense.id,
            'debit': 50,
            'credit': 0,
            'tax_ids': [(6, 0, self.tax_price_purchase_5.ids)]
        },
        {
            'account_id': self.default_account_tax_purchase.id,
            'debit': 2.5,
            'credit': 0,
            'tax_repartition_line_id': self.tax_repartition_line_purchase_5.id,
        }]
        journal_entry_2_vendor_a = self._init_journal_entry(self.vendor_a, datetime(2021, 8, 13, 12, 0), self.default_journal_purchase, items=journal_items_2)
        """
        |------------|
        |Expect value|
        |------------|

                                    | Net | Tax |
        ----------------------------|-----|-----|
        Sale                        | 0   | 0   |
        ----------------------------|-----|-----|
        Purchase                    | 0   | 0   |
            5% purchase (5.0)       | 50  | 2.5 |
            10% purchase (10.0)     | 150 | 15  |
        ----------------------------|-----|-----|
        """
        lines = self._get_lines_report(self.AccountTaxReport, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Sale', 0, 0),
            ('Purchase', 0, 0),
            ('5% purchase (5.0)', 50, 2.5),
            ('10% purchase (10.0)', 150, 15),
        ]
        self._check_report_value(lines, table_value)
        
    def test_02_validate_tax_report(self):
        # 13/08/2021 Create customer invoice 100 for customer a, tax 10%
        journal_items_1 = [{
            'account_id': self.default_account_revenue.id,
            'debit': 0,
            'credit': 100,
            'date_maturity': date(2021, 8, 13),
            'tax_ids': [(6, 0, self.tax_price_sale_10.ids)]
        },
        {
            'account_id': self.default_account_receivable.id,
            'debit': 110,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
        },
        {
            'account_id': self.default_account_tax_sale.id,
            'debit': 0,
            'credit': 10,
            'tax_repartition_line_id': self.tax_repartition_line_sale_10.id,
        }]
        journal_entry_1_customer_a = self._init_journal_entry(self.customer_a, datetime(2021, 8, 13, 12, 0), self.default_journal_sale, items=journal_items_1)
        """
        |------------|
        |Expect value|
        |------------|

                                    | Net | Tax |
        ----------------------------|-----|-----|
        Sale                        | 0   | 0   |
            10% sale (10.0)         | 100 | 10  |
        ----------------------------|-----|-----|
        Purchase                    | 0   | 0   |
        ----------------------------|-----|-----|
        """
        lines = self._get_lines_report(self.AccountTaxReport, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Sale', 0, 0),
            ('10% sale (10.0)', 100, 10),
            ('Purchase', 0, 0),
        ]
        self._check_report_value(lines, table_value)
        
        # Change the main value form 100 to 150
        journal_entry_1_customer_a.button_draft()
        journal_items_new_1 = [{
            'account_id': self.default_account_revenue.id,
            'debit': 0,
            'credit': 150,
            'date_maturity': date(2021, 8, 13),
            'tax_ids': [(6, 0, self.tax_price_sale_10.ids)]
        },
        {
            'account_id': self.default_account_receivable.id,
            'debit': 165,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
        },
        {
            'account_id': self.default_account_tax_sale.id,
            'debit': 0,
            'credit': 15,
            'tax_repartition_line_id': self.tax_repartition_line_sale_10.id,
        }]
        journal_entry_new_1_customer_a = self._init_journal_entry(self.customer_a, datetime(2021, 8, 13, 12, 0),
                                                              self.default_journal_sale, items=journal_items_new_1)
        """
        |------------|
        |Expect value|
        |------------|

                                    | Net | Tax |
        ----------------------------|-----|-----|
        Sale                        | 0   | 0   |
            10% sale (10.0)         | 150 | 15  |
        ----------------------------|-----|-----|
        Purchase                    | 0   | 0   |
        ----------------------------|-----|-----|
        """
        lines = self._get_lines_report(self.AccountTaxReport, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Sale', 0, 0),
            ('10% sale (10.0)', 150, 15),
            ('Purchase', 0, 0),
        ]
        self._check_report_value(lines, table_value)

        # Create customer invoice 50 for customer a, tax 5%
        journal_items_2 = [{
            'account_id': self.default_account_revenue.id,
            'debit': 0,
            'credit': 50,
            'date_maturity': date(2021, 8, 13),
            'tax_ids': [(6, 0, self.tax_price_sale_5.ids)]
        },
        {
            'account_id': self.default_account_receivable.id,
            'debit': 52.5,
            'credit': 0,
            'date_maturity': date(2021, 8, 13),
        },
        {
            'account_id': self.default_account_tax_sale.id,
            'debit': 0,
            'credit': 2.5,
            'tax_repartition_line_id': self.tax_repartition_line_sale_5.id,
        }]
        journal_entry_2_customer_a = self._init_journal_entry(self.customer_a, datetime(2021, 8, 13, 12, 0), self.default_journal_sale, items=journal_items_2)
        """
        |------------|
        |Expect value|
        |------------|

                                    | Net | Tax |
        ----------------------------|-----|-----|
        Sale                        | 0   | 0   |
            5% sale (5.0)           | 50  | 2.5 |
            10% sale (10.0)         | 150 | 15  |
        ----------------------------|-----|-----|
        Purchase                    | 0   | 0   |
        ----------------------------|-----|-----|
        """
        lines = self._get_lines_report(self.AccountTaxReport, datetime(2021, 8, 13, 12, 0), 'this_year')
        table_value = [
            ('Sale', 0, 0),
            ('5% sale (5.0)', 50, 2.5),
            ('10% sale (10.0)', 150, 15),
            ('Purchase', 0, 0),
        ]
        self._check_report_value(lines, table_value)
