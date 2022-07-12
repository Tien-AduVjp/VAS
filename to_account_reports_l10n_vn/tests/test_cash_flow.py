from datetime import datetime, date
from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class CashFlow(Common):

    def setUp(self):
        super(CashFlow, self).setUp()
        self.AccountCashFlowReport = self.env.ref('to_account_reports_l10n_vn.af_dynamic_report_cashsummary_vn')

    def test_01_validate_cash_flow(self):
        # 01/08/2021    # 01a
        journal_items_01a = [{
            'account_id': self.default_account_1111_01.id,
            'debit': 55000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 0,
            'credit': 50000,
            'tax_ids': [(6, 0, self.tax_price_vn_sale_10.ids)]
        },
        {
            'account_id': self.default_account_33311.id,
            'debit': 0,
            'credit': 5000,
            'tax_repartition_line_id': self.tax_repartition_line_vn_sale_10.id,
        }]
        journal_entry_01a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_01a)

        bank_stmt_items_01a = [{
            'account_id': self.default_account_1111.id,
            'debit': 55000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1111_01.id,
            'debit': 0,
            'credit': 55000
        }]
        bank_stmt_01a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_01a)
        (journal_entry_01a | bank_stmt_01a).line_ids.filtered(lambda r:r.account_id.code == '1111-01').reconcile()

        # 01/08/2021    # 01b
        journal_items_01b = [{
            'account_id': self.default_account_131.id,
            'debit': 45000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 0,
            'credit': 40000,
        },
        {
            'account_id': self.default_account_3331.id,
            'debit': 0,
            'credit': 5000,
        },
        {
            'account_id': self.default_account_1111_01.id,
            'debit': 45000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0,
            'credit': 45000,
        }]
        journal_entry_01b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_01b)
        journal_entry_01b.line_ids.filtered(lambda r: r.account_id.code.startswith('131')).reconcile()

        bank_stmt_items_01b = [{
            'account_id': self.default_account_1111.id,
            'debit': 45000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1111_01.id,
            'debit': 0,
            'credit': 45000
        }]
        bank_stmt_01b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_01b)
        (journal_entry_01b | bank_stmt_01b).line_ids.filtered(lambda r:r.account_id.code == '1111-01').reconcile()

        # 01/08/2021 02a
        journal_items_02a = [{
            'account_id': self.default_account_1111_02.id,
            'debit': 0,
            'credit': 66000,
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 60000,
            'credit': 0,
            'tax_ids': [(6, 0, self.tax_price_vn_purchase_10.ids)]
        },
        {
            'account_id': self.default_account_1331.id,
            'debit': 6000,
            'credit': 0,
            'tax_repartition_line_id': self.tax_repartition_line_vn_purchase_10.id,
        }]
        journal_entry_02a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_purchase, items=journal_items_02a)

        bank_stmt_items_02a = [{
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 66000
        },
        {
            'account_id': self.default_account_1111_02.id,
            'debit': 66000,
            'credit': 0
        }]
        bank_stmt_02a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_02a)
        (journal_entry_02a | bank_stmt_02a).line_ids.filtered(lambda r:r.account_id.code == '1111-02').reconcile()

        # 01/08/2021 02b
        # Mua hàng
        journal_items_02b_1 = [{
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 44000,
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 40000,
            'credit': 0,
            'tax_ids': [(6, 0, self.tax_price_vn_purchase_10.ids)]
        },
        {
            'account_id': self.default_account_1331.id,
            'debit': 4000,
            'credit': 0,
            'tax_repartition_line_id': self.tax_repartition_line_vn_purchase_10.id,
        }]
        # Trả NCC
        journal_items_02b_2 = [{
            'account_id': self.default_account_1111_02.id,
            'debit': 0,
            'credit': 44000,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 44000,
            'credit': 0,
        }]
        journal_entry_02b_1 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_purchase, items=journal_items_02b_1)
        journal_entry_02b_2 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_purchase, items=journal_items_02b_2)
        (journal_entry_02b_1 | journal_entry_02b_2).line_ids.filtered(lambda r: r.account_id.code.startswith('331')).reconcile()

        bank_stmt_items_02b = [{
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 44000
        },
        {
            'account_id': self.default_account_1111_02.id,
            'debit': 44000,
            'credit': 0
        }]
        bank_stmt_02b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_02b)
        (journal_entry_02b_2 | bank_stmt_02b).line_ids.filtered(lambda r:r.account_id.code == '1111-02').reconcile()

        # 01/08/2021 03
        journal_items_03= [{
            'account_id': self.default_account_3341.id,
            'debit': 500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 500000,
        }]
        journal_entry_03 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_03)

        bank_stmt_items_03 = [{
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 500000
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 500000,
            'credit': 0
        }]
        bank_stmt_03 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_03)
        (journal_entry_03 | bank_stmt_03).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021 04
        journal_items_04 = [{
            'account_id': self.default_account_635.id,
            'debit': 10000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_borrowing_loan.ids)]
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 10000,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 10000,
            'credit': 0,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 10000,
            'partner_id': self.vendor_a.id,
        }]
        journal_entry_04 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_04)
        journal_entry_04.line_ids.filtered(lambda r: r.account_id.code.startswith('331')).reconcile()

        bank_stmt_items_04 = [{
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 10000
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 10000,
            'credit': 0
        }]
        bank_stmt_04 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_04)
        (journal_entry_04 | bank_stmt_04).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021 05
        journal_items_05 = [{
            'account_id': self.default_account_3334.id,
            'debit': 15000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 15000,
        }]
        journal_entry_05 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_05)

        bank_stmt_items_05 = [{
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 15000
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 15000,
            'credit': 0
        }]
        bank_stmt_05 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_05)
        (journal_entry_05 | bank_stmt_05).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021 21a
        journal_items_21a = [{
            'account_id': self.default_account_2112.id,
            'debit': 500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 500000,
        }]
        journal_entry_21a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_21a)

        bank_stmt_items_21a = [{
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 500000
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 500000,
            'credit': 0
        }]
        bank_stmt_21a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_21a)
        (journal_entry_21a | bank_stmt_21a).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021 21b
        journal_items_21b = [{
            'account_id': self.default_account_2112.id,
            'debit': 500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 500000,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 500000,
            'credit': 0,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 500000,
        }]
        journal_entry_21b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_21b)
        journal_entry_21b.line_ids.filtered(lambda r: r.account_id.code.startswith('331')).reconcile()

        bank_stmt_items_21b = [{
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 500000
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 500000,
            'credit': 0
        }]
        bank_stmt_21b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_21b)
        (journal_entry_21b | bank_stmt_21b).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021 22a
        journal_items_22a = [{
            'account_id': self.default_account_1111_01.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_711.id,
            'debit': 0,
            'credit': 50000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_fixed_assets.ids)]
        }]
        journal_entry_22a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_22a)

        bank_stmt_items_22a = [{
            'account_id': self.default_account_1111.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1111_01.id,
            'debit': 0,
            'credit': 50000
        }]
        bank_stmt_22a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_22a)
        (journal_entry_22a | bank_stmt_22a).line_ids.filtered(lambda r:r.account_id.code == '1111-01').reconcile()

        # # 01/08/2021 22b
        journal_items_22b = [{
            'account_id': self.default_account_131.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_711.id,
            'debit': 0,
            'credit': 50000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_fixed_assets.ids)]
        },
        {
            'account_id': self.default_account_1111_01.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0,
            'credit': 50000,
        }]
        journal_entry_22b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_22b)
        journal_entry_22b.line_ids.filtered(lambda r: r.account_id.code.startswith('131')).reconcile()

        bank_stmt_items_22b = [{
            'account_id': self.default_account_1111.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1111_01.id,
            'debit': 0,
            'credit': 50000
        }]
        bank_stmt_22b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_22b)
        (journal_entry_22b | bank_stmt_22b).line_ids.filtered(lambda r:r.account_id.code == '1111-01').reconcile()

        # 01/08/2021    22c
        journal_items_22c = [{
            'account_id': self.default_account_811.id,
            'debit': 20000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_fixed_assets.ids)]
        },
        {
            'account_id': self.default_account_1111_02.id,
            'debit': 0,
            'credit': 20000,
        }]
        journal_entry_22c = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_22c)

        bank_stmt_items_22c = [{
            'account_id': self.default_account_1111_02.id,
            'debit': 20000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 20000
        }]
        bank_stmt_22c = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_22c)
        (journal_entry_22c | bank_stmt_22c).line_ids.filtered(lambda r:r.account_id.code == '1111-02').reconcile()

        # 01/08/2021 22d
        journal_items_22d = [{
            'account_id': self.default_account_811.id,
            'debit': 20000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_fixed_assets.ids)]
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 20000,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 20000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1111_02.id,
            'debit': 0,
            'credit': 20000,
        }]
        journal_entry_22d = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_22d)
        journal_entry_22d.line_ids.filtered(lambda r: r.account_id.code.startswith('331')).reconcile()

        bank_stmt_items_22d = [{
            'account_id': self.default_account_1111_02.id,
            'debit': 20000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 20000
        }]
        bank_stmt_22d = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_cash, items=bank_stmt_items_22d)
        (journal_entry_22d | bank_stmt_22d).line_ids.filtered(lambda r:r.account_id.code == '1111-02').reconcile()

        # 01/08/2021    23
        journal_items_23 = [{
            'account_id': self.default_account_1288.id,
            'debit': 50000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_lending_loan.ids)]
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 50000
        }]
        journal_entry_23 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_23)

        bank_stmt_items_23 = [{
            'account_id': self.default_account_1125_02.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 50000
        }]
        bank_stmt_23 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_23)
        (journal_entry_23 | bank_stmt_23).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021    24
        journal_items_24 = [{
            'account_id': self.default_account_1125_01.id,
            'debit': 60000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1283.id,
            'debit': 0,
            'credit': 60000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_lending_loan.ids)]
        }]
        journal_entry_24 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_24)

        bank_stmt_items_24 = [{
            'account_id': self.default_account_1125.id,
            'debit': 60000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125_01.id,
            'debit': 0,
            'credit': 60000
        }]
        bank_stmt_24 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_24)
        (journal_entry_24 | bank_stmt_24).line_ids.filtered(lambda r:r.account_id.code == '1125-01').reconcile()

        # 01/08/2021    25a
        journal_items_25a = [{
            'account_id': self.default_account_221.id,
            'debit': 700000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 700000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_lending_loan.ids)]
        }]
        journal_entry_25a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_25a)

        bank_stmt_items_25a = [{
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 700000
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 700000,
            'credit': 0
        }]
        bank_stmt_25a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_25a)
        (journal_entry_25a | bank_stmt_25a).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021    25b
        journal_items_25b = [{
            'account_id': self.default_account_221.id,
            'debit': 400000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 400000,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 400000,
            'credit': 0,
            'partner_id': self.vendor_a.id,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 400000,
        }]
        journal_entry_25b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_25b)
        journal_entry_25b.line_ids.filtered(lambda r: r.account_id.code.startswith('331')).reconcile()

        bank_stmt_items_25b = [{
            'account_id': self.default_account_1125_02.id,
            'debit': 400000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 400000
        }]
        bank_stmt_25b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_25b)
        (journal_entry_25b | bank_stmt_25b).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021
        journal_items_26a = [{
            'account_id': self.default_account_1125_01.id,
            'debit': 700000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_221.id,
            'debit': 0,
            'credit': 700000,
        }]
        journal_entry_26a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_26a)

        bank_stmt_items_26a = [{
            'account_id': self.default_account_1125.id,
            'debit': 700000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125_01.id,
            'debit': 0,
            'credit': 700000
        }]
        bank_stmt_26a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_26a)
        (journal_entry_26a | bank_stmt_26a).line_ids.filtered(lambda r:r.account_id.code == '1125-01').reconcile()

        # 01/08/2021
        journal_items_26b = [{
            'account_id': self.default_account_131.id,
            'debit': 700000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_221.id,
            'debit': 0,
            'credit': 700000,
        },
        {
            'account_id': self.default_account_1125_01.id,
            'debit': 700000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0,
            'credit': 700000,
            'partner_id': self.customer_a.id,
        }]
        journal_entry_26b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_26b)
        journal_entry_26b.line_ids.filtered(lambda r: r.account_id.code.startswith('131')).reconcile()

        bank_stmt_items_26b = [{
            'account_id': self.default_account_1125.id,
            'debit': 700000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125_01.id,
            'debit': 0,
            'credit': 700000
        }]
        bank_stmt_26b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_26b)
        (journal_entry_26b | bank_stmt_26b).line_ids.filtered(lambda r:r.account_id.code == '1125-01').reconcile()

        # 01/08/2021    27a
        journal_items_27a = [{
            'account_id': self.default_account_1125_01.id,
            'debit': 20000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_515.id,
            'debit': 0,
            'credit': 20000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_interests_dividends_distributed_profits.ids)]
        }]
        journal_entry_27a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_27a)

        bank_stmt_items_27a = [{
            'account_id': self.default_account_1125.id,
            'debit': 20000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125_01.id,
            'debit': 0,
            'credit': 20000
        }]
        bank_stmt_27a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_27a)
        (journal_entry_27a | bank_stmt_27a).line_ids.filtered(lambda r:r.account_id.code == '1125-01').reconcile()

        # 01/08/2021    27b
        journal_items_27b = [{
            'account_id': self.default_account_131.id,
            'debit': 30000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_515.id,
            'debit': 0,
            'credit': 30000,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_interests_dividends_distributed_profits.ids)]
        },
        {
            'account_id': self.default_account_1125_01.id,
            'debit': 30000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0,
            'credit': 30000,
            'partner_id': self.customer_a.id,
        }]
        journal_entry_27b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_27b)
        journal_entry_27b.line_ids.filtered(lambda r: r.account_id.code.startswith('131')).reconcile()

        bank_stmt_items_27b = [{
            'account_id': self.default_account_1125.id,
            'debit': 30000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125_01.id,
            'debit': 0,
            'credit': 30000
        }]
        bank_stmt_27b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_27b)
        (journal_entry_27b | bank_stmt_27b).line_ids.filtered(lambda r:r.account_id.code == '1125-01').reconcile()

        # 01/08/2021    31
        journal_items_31 = [{
            'account_id': self.default_account_1125_01.id,
            'debit': 500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4111.id,
            'debit': 0,
            'credit': 500000,
        }]
        journal_entry_31 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_31)

        bank_stmt_items_31 = [{
            'account_id': self.default_account_1125.id,
            'debit': 500000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125_01.id,
            'debit': 0,
            'credit': 500000
        }]
        bank_stmt_31 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_31)
        (journal_entry_31 | bank_stmt_31).line_ids.filtered(lambda r:r.account_id.code == '1125-01').reconcile()

        # 01/08/2021    32
        journal_items_32 = [{
            'account_id': self.default_account_4111.id,
            'debit': 200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 200000,
        }]
        journal_entry_32 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_32)

        bank_stmt_items_32 = [{
            'account_id': self.default_account_1125_02.id,
            'debit': 200000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 200000
        }]
        bank_stmt_32 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_32)
        (journal_entry_32 | bank_stmt_32).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021    33
        journal_items_33 = [{
            'account_id': self.default_account_1125_01.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3411.id,
            'debit': 0,
            'credit': 100000,
        }]
        journal_entry_33 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_33)

        bank_stmt_items_33 = [{
            'account_id': self.default_account_1125.id,
            'debit': 100000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125_01.id,
            'debit': 0,
            'credit': 100000
        }]
        bank_stmt_33 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_33)
        (journal_entry_33 | bank_stmt_33).line_ids.filtered(lambda r:r.account_id.code == '1125-01').reconcile()

        # 01/08/2021
        journal_items_34 = [{
            'account_id': self.default_account_3411.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 100000,
        }]
        journal_entry_34 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_34)

        bank_stmt_items_34 = [{
            'account_id': self.default_account_1125_02.id,
            'debit': 100000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 100000
        }]
        bank_stmt_34 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_34)
        (journal_entry_34 | bank_stmt_34).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021    35
        journal_items_35 = [{
            'account_id': self.default_account_3412.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 50000,
        }]
        journal_entry_35 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_35)

        bank_stmt_items_35 = [{
            'account_id': self.default_account_1125_02.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 50000
        }]
        bank_stmt_35 = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_35)
        (journal_entry_35 | bank_stmt_35).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021
        journal_items_36a = [{
            'account_id': self.default_account_4212.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 50000,
        }]
        journal_entry_36a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_36a)

        bank_stmt_items_36a = [{
            'account_id': self.default_account_1125_02.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 50000
        }]
        bank_stmt_36a = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_36a)
        (journal_entry_36a | bank_stmt_36a).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 01/08/2021
        journal_items_36b = [{
            'account_id': self.default_account_4212.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3388.id,
            'debit': 0,
            'credit': 50000,
            'partner_id': self.vendor_b.id,
        },
        {
            'account_id': self.default_account_3388.id,
            'debit': 50000,
            'credit': 0,
            'partner_id': self.vendor_b.id,
        },
        {
            'account_id': self.default_account_1125_02.id,
            'debit': 0,
            'credit': 50000,
        }]
        journal_entry_36b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_36b)
        journal_entry_36b.line_ids.filtered(lambda r: r.account_id.code.startswith('3388')).reconcile()

        bank_stmt_items_36b = [{
            'account_id': self.default_account_1125_02.id,
            'debit': 50000,
            'credit': 0
        },
        {
            'account_id': self.default_account_1125.id,
            'debit': 0,
            'credit': 50000
        }]
        bank_stmt_36b = self._init_journal_entry(None , datetime(2021, 8, 1, 12, 0), self.default_journal_vn_bank, items=bank_stmt_items_36b)
        (journal_entry_36b | bank_stmt_36b).line_ids.filtered(lambda r:r.account_id.code == '1125-02').reconcile()

        # 09/08/2020
        journal_items_60 = [{
            'account_id': self.default_account_1125.id,
            'debit': 150000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4111.id,
            'debit': 0,
            'credit': 150000,
        }]
        journal_entry_60 = self._init_journal_entry(None , datetime(2020, 8, 9, 12, 0), self.default_journal_vn_misc, items=journal_items_60)
        lines = self._get_lines_report(self.AccountCashFlowReport, datetime(2021, 12, 30, 12, 0))
        table_value = [
            ('I. Cash flows from operating activities', 0),
            ('1a. Proceeds from sales and services rendered and other revenues (Cash Direct)', 50000),
            ('1b. Proceeds from sales and services rendered and other revenues (via receivables)', 45000),
            ('Total 1. Proceeds from sales and services rendered and other revenues', 95000),
            ('2.a. Expenditures paid to suppliers (Cash Direct)', -66000),
            ('2.b. Expenditures paid to suppliers (Via Payables)', -44000),
            ('Total 2. Expenditures paid to suppliers', -110000),
            ('3. Expenditures paid to employees', -500000),
            ('4. Paid interests', -10000),
            ('5. Paid enterprise income tax', -15000),
            ('6.a. Total Cash Received', 2310000),
            ('6.b. Total Cash Received which was classified into other items', 1605000),
            ('Total 6. Other proceeds from operating activities', 705000),
            ('7.a. Total Cash Out', -3275000),
            ('7.b. Total Cash Out which was classified into other items', -2775000),
            ('Total 7. Other expenditures on operating activities', -500000),
            ('Total Net cash flows from operating activities', -335000),
            ('II. Cash flows from investing activities', 0),
            ('1.a. Expenditures on purchase and construction of fixed assets and long-term assets (Cash Direct)', 0),
            ('1.b. Expenditures on purchase and construction of fixed assets and long-term assets (Via Payables)', -500000),
            ('Total 1. Expenditures on purchase and construction of fixed assets and long-term assets', -500000),
            ('2.a. Sales Revenue of fixed assets and other long-term assets (Cash Direct)', 50000),
            ('2.b. Sales Revenue of fixed assets and other long-term assets (Via Receivables)', 50000),
            ('2.c. Sales/Disposal Expenses of fixed assets and other long-term assets (Cash Direct)', -20000),
            ('2.d. Sales/Disposal Expenses of fixed assets and other long-term assets (Via Payables)', -20000),
            ('Total 2. Proceeds from disposal or transfer of fixed assets and other long-term assets', 60000),
            ('3. Expenditures on loans and purchase of  debt instruments from other entities', -50000),
            ('4. Proceeds from lending or repurchase of debt instruments from other entities', 60000),
            ('5.a. Expenditures on equity investments in other entities (Cash Direct)', -700000),
            ('5.b. Expenditures on equity investments in other entities (Via Payables)', -400000),
            ('Total 5. Expenditures on equity investments in other entities', -1100000),
            ('6.a. Proceed from equity investments in other entities (Cash Direct)', 0),
            ('6.b Proceed from equity investments in other entities (Via receivables)', 700000),
            ('Total 6. Proceed from equity investments in other entities', 700000),
            ('7.a. Proceed from interests, dividends and distributed profits (Cash Direct)', 20000),
            ('7.b. Proceed from interests, dividends and distributed profits (Via Receivables)', 30000),
            ('Total 7. Proceed from interests, dividends and distributed profits', 50000),
            ('Total Net cash flows from investing activities', -780000),
            ('III. Cash flows from financial activities', 0),
            ('1. Proceeds from issuance of shares and receipt of contributed capital', 500000),
            ('2. Repayment of contributed capital and repurchase of stock issued', -200000),
            ('3. Proceeds from borrowings', 100000),
            ('4. Repayment of principal', -100000),
            ('5. Repayment of financial principal', -50000),
            ('6.a. Dividends and profits paid to owners (Cash Direct)', -50000),
            ('6.b. Dividends and profits paid to owners (Via Payables)', -50000),
            ('Total 6. Dividends and profits paid to owners', -100000),
            ('Total Cash flows from financial activities', 150000),
            ('Total Net cash flows during the fiscal year (50 = 20+30+40)', -965000),
            ('Cash and cash equivalents, beginning of fiscal year', 150000),
            ('Effect of exchange rate fluctuations', 0),
            ('Cash and cash equivalents, end of fiscal year (70 = 50 + 60 + 61)', -815000), # -965000 + 150000
        ]
        self._check_report_value(lines, table_value)
