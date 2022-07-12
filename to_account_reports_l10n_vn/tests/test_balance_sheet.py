from datetime import datetime, date
from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class BalanceSheet(Common):

    def setUp(self):
        super(BalanceSheet, self).setUp()
        self.AccountBalanceSheetReport = self.env.ref('to_account_reports_l10n_vn.af_dynamic_report_balancesheet_vn')

    def test_01_validate_balance_sheet(self):
        """
        |------------|
        |Expect value|
        |------------|
        Line items                                                                  | Code | Note | As of time |
        ----------------------------------------------------------------------------|------|------|------------|
        Total A - CURRENT ASSETS                                                    | 100  |      |            |
        (100 = 110 + 120 + 130 + 140 + 150)                                         |      |      |            |
            Total I. Cash and Cash Equivalents                                      | 110  |      |            |
            (110 = 111 + 112)                                                       |      |      |            |
                1. Bank & Cash                                                      | 111  |      |            |
                2. Cash equivalents                                                 | 112  |      |            |
            Total II. Cash flows from investing activities                          | 120  |      |            |
            (120 = 121 + 122 + 123)                                                 |      |      |            |
                1. Trading securities                                               | 121  |      |            |
                2. Allowances for decline in value of trading securities            | 122  |      |            |
                3. Held to maturity investments                                     | 123  |      |            |
            Total III. Short-term receivables                                       | 130  |      |            |
            (130 = 131 + 132 + 133 + 134 + 135 + 136 + 137 + 139)                   |      |      |            |
                1. Short-term trade receivables                                     | 131  |      |            |
                2. Short-term prepayments to suppliers                              | 132  |      |            |
                3. Short-term intra-company receivables                             | 133  |      |            |
                4. Receivables under schedule of construction contract              | 134  |      |            |
                5. Short-term loan receivables                                      | 135  |      |            |
                6. Other short-term receivables                                     | 136  |      |            |
                7. Short-term allowances for doubtful debts                         | 137  |      |            |
                8. Shortage of assets awaiting resolution                           | 139  |      |            |
            Total IV. Inventories (140 = 141 + 149)                                 | 140  |      |            |
                Total 1. Inventories                                                | 141  |      |            |
                    1.a. All Inventories                                            | 141a |      |            |
                    1.b. Minus Long-term work in progress                           | 141b |      |            |
                    1.c. Minus Long-term equipment and spare parts for replacement  | 141c |      |            |
                2. Allowances for decline in value of inventories                   | 149  |      |            |
            Total V. Other current assets (150 = 151 + 152 + 153 + 154 + 155)       | 150  |      |            |
                1. Short-term prepaid expenses                                      | 151  |      |            |
                2. Deductible VAT                                                   | 152  |      |            |
                3. Taxes and other receivables from government budget               | 153  |      |            |
                4. Government bonds purchased for resale                            | 154  |      |            |
                5. Other current assets                                             | 155  |      |            |
        Total B - NON-CURRENT ASSETS (200 = 210 + 220 + 240 + 250 + 260)            | 200  |      |            |
            Total I. Long-term receivables                                          | 210  |      |            |
            (210 = 211 + 212 + 213 + 214 + 215 + 216 + 219)                         |      |      |            |
                1. Long-term trade receivables                                      | 211  |      |            |
                2. Long-term prepayments to suppliers                               | 212  |      |            |
                3. Working capital provided to sub-units                            | 213  |      |            |
                4. Long-term intra-company receivables                              | 214  |      |            |
                5. Long-term loan receivables                                       | 215  |      |            |
                Total 6. Other long-term receivables                                | 216  |      |            |
                    6a. Other long-term receivables (assets)                        |      |      |            |
                    6b. Other long-term receivables (equity)                        |      |      |            |
                7. Long-term allowances for doubtful debts                          | 219  |      |            |
            Total II. Fixed assets (220 = 221 + 224 + 227 + 230)                    | 220  |      |            |
                Total 1. Tangible fixed assets (221 = 222 + 223)                    | 221  |      |            |
                    - Historical costs                                              | 222  |      |            |
                    - Accumulated depreciation                                      | 223  |      |            |
                Total 2. Finance lease fixed assets (224 = 225 + 226)               | 224  |      |            |
                    - Historical costs                                              | 225  |      |            |
                    - Accumulated depreciation                                      | 226  |      |            |
                Total 3. Intangible fixed assets (227 = 228 + 229)                  | 227  |      |            |
                    - Historical costs                                              | 228  |      |            |
                    - Accumulated depreciation                                      | 229  |      |            |
            Total III. Investment properties (230 = 231 + 232)                      | 230  |      |            |
                - Historical costs                                                  | 231  |      |            |
                - Accumulated depreciation                                          | 232  |      |            |
            Total IV. Long-term assets in progress (240 = 241 + 242)                | 240  |      |            |
                1. Long-term work in progress                                       | 241  |      |            |
                2. Construction in progress                                         | 242  |      |            |
            Total V. Long-term investments (250 = 251 + 252 + 253 + 254 + 255)      | 250  |      |            |
                1. Investments in subsidiaries                                      | 251  |      |            |
                2. Investments in joint ventures and associates                     | 252  |      |            |
                3. Investments in equity of other entities                          | 253  |      |            |
                4. Allowances for long-term investments                             | 254  |      |            |
                5. Held to maturity investments                                     | 255  |      |            |
            Total VI. Other long-term assets (260 = 261 + 262 + 263 + 268)          | 260  |      |            |
                1. Long-term prepaid expenses                                       | 261  |      |            |
                2. Deferred income tax assets                                       | 262  |      |            |
                3. Long-term equipment and spare parts for replacement              | 263  |      |            |
                4. Other long-term assets                                           | 268  |      |            |
        TOTAL ASSETS (270 = 100 + 200)                                              | 270  |      |            |
        Total C - LIABILITIES (300 = 310 + 330)                                     | 300  |      |            |
            Total I. Short-term liabilities                                         | 310  |      |            |
            (310 = 311 + 312 + 313 + 314 + 315                                      |      |      |            |
             + 316 + 317 + 318 + 319 + 320 + 321 + 322 + 323 + 324)                 |      |      |            |
                1. Short-term trade payables                                        | 311  |      |            |
                2. Short-term prepayments from customers                            | 312  |      |            |
                3. Taxes and other payables to government budget                    | 313  |      |            |
                4. Payables to employees                                            | 314  |      |            |
                5. Short-term accrued expenses                                      | 315  |      |            |
                6. Short-term intra-company payables                                | 316  |      |            |
                7. Payables under schedule of construction contract                 | 317  |      |            |
                8. Short-term unearned revenues                                     | 318  |      |            |
                9. Other short-term payments                                        | 319  |      |            |
                10. Short-term borrowings and finance lease liabilities             | 320  |      |            |
                11. Short-term provisions                                           | 321  |      |            |
                12. Bonus and welfare fund                                          | 322  |      |            |
                13. Price stabilization fund                                        | 323  |      |            |
                14. Government bonds purchased for resale                           | 324  |      |            |
            Total II. Long-term liabilities                                         | 330  |      |            |
            (330 = 331 + 332 + 333 + 334 + 335 + 336 + 337                          |      |      |            |
             + 338 + 339 + 340 + 341 + 342 + 343)                                   |      |      |            |
                1. Long-term trade payables                                         | 331  |      |            |
                2. Long-term prepayments from customers                             | 332  |      |            |
                3. Long-term accrued expenses                                       | 333  |      |            |
                4. Intra-company payables for operating capital received            | 334  |      |            |
                5. Long-term intra-company payables                                 | 335  |      |            |
                6. Long-term unearned revenues                                      | 336  |      |            |
                7. Other long-term payables                                         | 337  |      |            |
                8. Long-term borrowings and finance lease liabilities               | 338  |      |            |
                9. Convertible bonds                                                | 339  |      |            |
                10. Preference shares                                               | 340  |      |            |
                11. Deferred income tax payables                                    | 341  |      |            |
                12. Long-term provisions                                            | 342  |      |            |
                13. Science and technology development fund                         | 343  |      |            |
        Total D - OWNER’S EQUITY (400 = 410 + 430)                                  | 400  |      |            |
            Total I. Owner’s equity                                                 | 410  |      |            |
            (410 = 411 + 412 + 413 + 414 + 415 + 416                                |      |      |            |
            + 417 + 418 + 419 + 420 + 421 + 422)                                    |      |      |            |
                Total 1. Contributed capital                                        | 411  |      |            |
                    - Ordinary shares with voting rights                            | 411a |      |            |
                    - Preference shares                                             | 411b |      |            |
                2. Capital surplus                                                  | 412  |      |            |
                3. Conversion options on convertible bonds                          | 413  |      |            |
                4. Other capital                                                    | 414  |      |            |
                5. Treasury shares                                                  | 415  |      |            |
                6. Differences upon asset revaluation                               | 416  |      |            |
                7. Exchange rate differences                                        | 417  |      |            |
                8. Development and investment funds                                 | 418  |      |            |
                9. Enterprise reorganization assistance fund                        | 419  |      |            |
                10. Other equity funds                                              | 420  |      |            |
                Total 11. Undistributed profit after tax                            | 421  |      |            |
                    - Undistributed profit after tax brought forward                | 421a |      |            |
                    - Undistributed profit after tax for the current year           | 421b |      |            |
                12. Capital expenditure funds                                       | 422  |      |            |
            Total II. Funding sources and other funds (430 = 431 + 432)             | 430  |      |            |
                1. Funding sources                                                  | 431  |      |            |
                2. Funds used for fixed asset acquisition                           | 432  |      |            |
        TOTAL EQUITY (440 = 300 + 400)                                              | 440  |      |            |
        ----------------------------------------------------------------------------|------|------|------------|
        """

        # 15/12/2020 5,000,000 in cash as a capital contribution
        journal_items_1 = [{
            'account_id': self.default_account_1111.id,
            'debit': 5000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4111.id,
            'debit': 0,
            'credit': 5000000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_1)

        # 01/12/2020 Make a cash deposit into account 4,000,000.
        journal_items_2 = [{
            'account_id': self.default_account_1121.id,
            'debit': 4000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 4000000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_2)

        # 25/12/2020 Buy foreign currency with VND account, transfer to USD account, foreign currency amount: 50 000 USD exchange rate 1 USD = 23,000 VND.
        journal_items_3 = [{
            'account_id': self.default_account_1122.id,
            'debit': 1150000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 1150000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 25, 12, 0), self.default_journal_vn_misc, items=journal_items_3)

        # 10/12/2020
        journal_items_4 = [{
            'account_id': self.default_account_1211.id,
            'debit': 450000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 450000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_4)

        # 05/12/2020
        journal_items_5 = [{
            'account_id': self.default_account_1281.id,
            'debit': 300000,
            'credit': 0,
            'date_maturity': date(2021, 2, 5),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 300000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 5, 12, 0), self.default_journal_vn_misc, items=journal_items_5)

        # 05/12/2020
        journal_items_6 = [{
            'account_id': self.default_account_1281.id,
            'debit': 500000,
            'credit': 0,
            'date_maturity': date(2021, 9, 5),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 500000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 5, 12, 0), self.default_journal_vn_misc, items=journal_items_6)

        # 05/12/2020
        journal_items_7 = [{
            'account_id': self.default_account_1281.id,
            'debit': 500000,
            'credit': 0,
            'date_maturity': date(2022, 12, 5),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 500000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 5, 12, 0), self.default_journal_vn_misc, items=journal_items_7)

        # 05/12/2020
        journal_items_8 = [{
            'account_id': self.default_account_331.id,
            'debit': 550000,
            'credit': 0,
            'date_maturity': date(2020, 12, 5),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 550000,
        }]
        self._init_journal_entry(self.vendor_b , datetime(2020, 12, 5, 12, 0), self.default_journal_vn_bank, items=journal_items_8)

        # 05/12/2020
        journal_items_9 = [{
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 1100000,
            'date_maturity': date(2021, 1, 15),
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 1000000,
            'credit': 0,
            'tax_ids': [(6, 0, self.tax_price_vn_purchase_10.ids)]
        },
        {
            'account_id': self.default_account_1331.id,
            'debit': 100000,
            'credit': 0,
            'tax_repartition_line_id': self.tax_repartition_line_vn_purchase_10.id,
        }]
        self._init_journal_entry(self.vendor_b , datetime(2020, 12, 6, 12, 0), self.default_journal_vn_bank, items=journal_items_9)

        # 05/12/2020
        journal_items_10 = [{
            'account_id': self.default_account_331.id,
            'debit': 550000,
            'credit': 0,
            'date_maturity': date(2022, 12, 5),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 550000,
        }]
        self._init_journal_entry(self.vendor_b , datetime(2020, 12, 5, 12, 0), self.default_journal_vn_bank, items=journal_items_10)

        # 07/12/2020
        journal_items_11 = [{
            'account_id': self.default_account_131.id,
            'debit': 1100000,
            'credit': 0,
            'date_maturity': date(2021, 1, 21),
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 0,
            'credit': 1000000,
            'tax_ids': [(6, 0, self.tax_price_vn_sale_10.ids)]
        },
        {
            'account_id': self.default_account_33311.id,
            'debit': 0,
            'credit': 100000,
            'tax_repartition_line_id': self.tax_repartition_line_vn_sale_10.id,
        },
        {
            'account_id': self.default_account_632.id,
            'debit': 500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 0,
            'credit': 500000,
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_911.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_911.id,
            'debit': 0,
            'credit': 1000000,
        },
        {
            'account_id': self.default_account_632.id,
            'debit': 0,
            'credit': 500000,
        },
        {
            'account_id': self.default_account_4212.id,
            'debit': 0,
            'credit': 500000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 7, 12, 0), self.default_journal_vn_misc, items=journal_items_11)

        # 07/12/2020
        journal_items_12 = [{
            'account_id': self.default_account_1121.id,
            'debit': 550000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0,
            'credit': 550000,
            'date_maturity': date(2020, 12, 7),
            'partner_id': self.customer_a.id,
        }]
        self._init_journal_entry(self.customer_a , datetime(2020, 12, 7, 12, 0), self.default_journal_vn_bank, items=journal_items_12)

        # 24/12/2020
        journal_items_13 = [{
            'account_id': self.default_account_337.id,
            'debit': 200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 0,
            'credit': 200000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 24, 12, 0), self.default_journal_vn_misc, items=journal_items_13)

        # 14/12/2020
        journal_items_14 = [{
            'account_id': self.default_account_1283.id,
            'debit': 50000,
            'credit': 0,
            'date_maturity': date(2021, 6, 14),
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_1111.id,
            'debit': 0,
            'credit': 50000,
            'partner_id': self.customer_a.id,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 14, 12, 0), self.default_journal_vn_misc, items=journal_items_14)

        # 10/12/2020
        journal_items_15 = [{
            'account_id': self.default_account_141.id,
            'debit': 10000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 10000,
            'partner_id': self.customer_a.id,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_15)

        # 31/12/2020
        journal_items_16 = [{
            'account_id': self.default_account_6426.id,
            'debit': 25000,
            'credit': 0,
            'date_maturity': date(2021, 6, 30),
        },
        {
            'account_id': self.default_account_2293.id,
            'debit': 0,
            'credit': 25000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_16)

        # 31/12/2020
        journal_items_17 = [{
            'account_id': self.default_account_1381.id,
            'debit': 1000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 0,
            'credit': 1000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_17)

        # 31/12/2020
        journal_items_18 = [{
            'account_id': self.default_account_6426.id,
            'debit': 80000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2294.id,
            'debit': 0,
            'credit': 80000,
            'date_maturity': date(2021, 6, 30),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_18)

        # 31/12/2020
        journal_items_19 = [{
            'account_id': self.default_account_242.id,
            'debit': 120000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_short_term_prepaid_expense.ids)]
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 120000,
        },
        {
            'account_id': self.default_account_242.id,
            'debit': 360000,
            'credit': 0,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_long_term_prepaid_expense.ids)]
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 360000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_19)

        # 20/12/2020
        journal_items_20 = [{
            'account_id': self.default_account_1368.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_20)

        # 20/12/2020
        journal_items_21 = [{
            'account_id': self.default_account_171.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 50000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_21)

        # 20/12/2020
        journal_items_22 = [{
            'account_id': self.default_account_2288.id,
            'debit': 200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 200000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_22)

        # 20/12/2020
        journal_items_23 = [{
            'account_id': self.default_account_131.id,
            'debit': 550000,
            'credit': 0,
            'partner_id': self.customer_a.id,
            'date_maturity': date(2022, 1, 1),
        },
        {
            'account_id': self.default_account_5111.id,
            'debit': 0,
            'credit': 500000,
            'tax_ids': [(6, 0, self.tax_price_vn_sale_10.ids)]
        },
        {
            'account_id': self.default_account_33311.id,
            'debit': 0,
            'credit': 50000,
            'tax_repartition_line_id': self.tax_repartition_line_vn_sale_10.id,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_23)

        # 20/12/2020
        journal_items_24 = [{
            'account_id': self.default_account_1368.id,
            'debit': 20000,
            'credit': 0,
            'date_maturity': date(2022, 6, 30),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 20000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_24)

        # 20/12/2020
        journal_items_25 = [{
            'account_id': self.default_account_1361.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1000000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_25)

        # 20/12/2020
        journal_items_26 = [{
            'account_id': self.default_account_1283.id,
            'debit': 40000,
            'credit': 0,
            'partner_id': self.customer_a.id,
            'date_maturity': date(2022, 12, 19),
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 40000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_26)

        # 20/12/2020
        journal_items_27 = [{
            'account_id': self.default_account_1388.id,
            'debit': 30000,
            'credit': 0,
            'partner_id': self.vendor_a.id,
            'date_maturity': date(2023, 12, 20),
        },
        {
            'account_id': self.default_account_2111.id,
            'debit': 0,
            'credit': 30000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_27)

        # 20/12/2020
        journal_items_28 = [{
            'account_id': self.default_account_6426.id,
            'debit': 80000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2293.id,
            'debit': 0,
            'credit': 80000,
            'date_maturity': date(2022, 12, 31),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_28)

        # 01/12/2020
        journal_items_29 = [{
            'account_id': self.default_account_2112.id,
            'debit': 1200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1200000,
        },
        {
            'account_id': self.default_account_6424.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2141.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_29)

        # 01/12/2020
        journal_items_30 = [{
            'account_id': self.default_account_2121.id,
            'debit': 1200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1200000,
        },
        {
            'account_id': self.default_account_632.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2142.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_30)

        # 01/12/2020
        journal_items_31 = [{
            'account_id': self.default_account_2131.id,
            'debit': 1200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1200000,
        },
        {
            'account_id': self.default_account_6424.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2143.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_31)

        # 01/12/2020
        journal_items_32 = [{
            'account_id': self.default_account_217.id,
            'debit': 1200000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1200000,
        },
        {
            'account_id': self.default_account_632.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2147.id,
            'debit': 0,
            'credit': 10000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_32)

        # 31/12/2020
        journal_items_33 = [{
            'account_id': self.default_account_635.id,
            'debit': 2500,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2291.id,
            'debit': 0,
            'credit': 2500,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_33)

        # 31/12/2020
        journal_items_34 = [{
            'account_id': self.default_account_6426.id,
            'debit': 25000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2294.id,
            'debit': 0,
            'credit': 25000,
            'date_maturity': date(2022, 12, 31),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_34)

        # 31/12/2020
        journal_items_35 = [{
            'account_id': self.default_account_2412.id,
            'debit': 45000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 45000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_35)

        # 31/12/2020
        journal_items_36 = [{
            'account_id': self.default_account_221.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1000000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_36)

        # 31/12/2020
        journal_items_37 = [{
            'account_id': self.default_account_222.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1000000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_37)

        # 31/12/2020
        journal_items_38 = [{
            'account_id': self.default_account_2281.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 1000000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_38)

        # 31/12/2020
        journal_items_39 = [{
            'account_id': self.default_account_6426.id,
            'debit': 20000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_2292.id,
            'debit': 0,
            'credit': 20000,
            'date_maturity': date(2025, 12, 31),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_39)

        # 20/12/2020
        journal_items_40 = [{
            'account_id': self.default_account_243.id,
            'debit': 15000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_8212.id,
            'debit': 0,
            'credit': 15000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_40)

        # 10/12/2018
        journal_items_41 = [{
            'account_id': self.default_account_2288.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None , datetime(2018, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_41)

        # 31/12/2020
        journal_items_43 = [{
            'account_id': self.default_account_6421.id,
            'debit': 18000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3341.id,
            'debit': 0,
            'credit': 18000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_43)

        # 31/12/2020
        journal_items_44 = [{
            'account_id': self.default_account_6421.id,
            'debit': 3780,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3383.id,
            'debit': 0,
            'credit': 3060,
        },
        {
            'account_id': self.default_account_3384.id,
            'debit': 0,
            'credit': 540,
        },
        {
            'account_id': self.default_account_3386.id,
            'debit': 0,
            'credit': 180,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_44)

        # 31/12/2020
        journal_items_45 = [{
            'account_id': self.default_account_6427.id,
            'debit': 5000,
            'credit': 0,
            'date_maturity': date(2021, 1, 10),
        },
        {
            'account_id': self.default_account_335.id,
            'debit': 0,
            'credit': 5000,
            'date_maturity': date(2021, 1, 10),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_45)

        # 10/12/2020
        journal_items_46 = [{
            'account_id': self.default_account_6427.id,
            'debit': 5000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 5000,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 10000,
            'credit': 0,
            'partner_id': self.customer_a.id,
        },
        {
            'account_id': self.default_account_3368.id,
            'debit': 0,
            'credit': 10000,
            'partner_id': self.customer_a.id,
            'date_maturity': date(2021, 1, 31),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_46)

        # 24/12/2020
        journal_items_47 = [{
            'account_id': self.default_account_131.id,
            'debit': 200000,
            'credit': 0,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2021, 3, 31),
        },
        {
            'account_id': self.default_account_337.id,
            'debit': 0,
            'credit': 200000,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2021, 3, 31),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 24, 12, 0), self.default_journal_vn_misc, items=journal_items_47)

        # 01/12/2020
        journal_items_48 = [{
            'account_id': self.default_account_131.id,
            'debit': 240000,
            'credit': 0,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2021, 2, 28),
        },
        {
            'account_id': self.default_account_3387.id,
            'debit': 0,
            'credit': 240000,
            'partner_id': self.customer_b.id,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_48)

        # 15/12/2020
        journal_items_49 = [{
            'account_id': self.default_account_1121.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3411.id,
            'debit': 0,
            'credit': 1000000,
            'date_maturity': date(2021, 3, 15),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_49)

        # 15/12/2020
        journal_items_50 = [{
            'account_id': self.default_account_6415.id,
            'debit': 16000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3521.id,
            'debit': 0,
            'credit': 16000,
            'date_maturity': date(2021, 3, 31),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_50)

        # 15/12/2020
        journal_items_51 = [{
            'account_id': self.default_account_4212.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3531.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_51)

        # 15/12/2020
        journal_items_52 = [{
            'account_id': self.default_account_632.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_357.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_52)

        # 15/12/2020
        journal_items_53 = [{
            'account_id': self.default_account_1121.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_171.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_53)

        # 31/12/2020
        journal_items_56 = [{
            'account_id': self.default_account_635.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_335.id,
            'debit': 0,
            'credit': 10000,
            'date_maturity': date(2022, 2, 28),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_56)

        # 20/12/2020
        journal_items_57 = [{
            'account_id': self.default_account_1121.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3361.id,
            'debit': 0,
            'credit': 1000000,
            'date_maturity': date(2022, 12, 20),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_57)

        # 06/12/2020
        journal_items_54 = [{
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 1100000,
            'date_maturity': date(2022, 1, 15),
        },
        {
            'account_id': self.default_account_1561.id,
            'debit': 1000000,
            'credit': 0,
            'tax_ids': [(6, 0, self.tax_price_vn_purchase_10.ids)]
        },
        {
            'account_id': self.default_account_1331.id,
            'debit': 100000,
            'credit': 0,
            'tax_repartition_line_id': self.tax_repartition_line_vn_purchase_10.id,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 6, 12, 0), self.default_journal_vn_misc, items=journal_items_54)

        # 10/12/2020
        journal_items_58 = [{
            'account_id': self.default_account_6427.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 0,
            'credit': 10000,
            'date_maturity': date(2022, 12, 31),
        },
        {
            'account_id': self.default_account_331.id,
            'debit': 10000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3368.id,
            'debit': 0,
            'credit': 10000,
            'date_maturity': date(2022, 12, 31),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 10, 12, 0), self.default_journal_vn_misc, items=journal_items_58)

        # 01/12/2020
        journal_items_59 = [{
            'account_id': self.default_account_131.id,
            'debit': 240000,
            'credit': 0,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2022, 12, 1),
        },
        {
            'account_id': self.default_account_3387.id,
            'debit': 0,
            'credit': 240000,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2022, 12, 1),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_59)

        # 01/12/2020
        journal_items_60 = [{
            'account_id': self.default_account_1121.id,
            'debit': 2000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_344.id,
            'debit': 0,
            'credit': 2000,
            'partner_id': self.customer_b.id,
            'date_maturity': date(2022, 12, 1),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_60)

        # 15/12/2020
        journal_items_62 = [{
            'account_id': self.default_account_1121.id,
            'debit': 1000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3432.id,
            'debit': 0,
            'credit': 1000000,
            'date_maturity': date(2022, 6, 15),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_62)

        # 15/12/2020
        journal_items_61 = [{
            'account_id': self.default_account_1121.id,
            'debit': 10000000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3411.id,
            'debit': 0,
            'credit': 10000000,
            'date_maturity': date(2023, 12, 15),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_61)

        # 15/12/2020
        journal_items_63 = [{
            'account_id': self.default_account_1121.id,
            'debit': 1300000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_41111.id,
            'debit': 0,
            'credit': 700000,
        },
        {
            'account_id': self.default_account_4112.id,
            'debit': 0,
            'credit': 100000,
        },
        {
            'account_id': self.default_account_41112.id,
            'debit': 0,
            'credit': 150000,
        },
        {
            'account_id': self.default_account_41112.id,
            'debit': 0,
            'credit': 150000,
        },
        {
            'account_id': self.default_account_4112.id,
            'debit': 0,
            'credit': 200000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_63)

        # 20/12/2020
        journal_items_64 = [{
            'account_id': self.default_account_8212.id,
            'debit': 15000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_347.id,
            'debit': 0,
            'credit': 15000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 20, 12, 0), self.default_journal_vn_misc, items=journal_items_64)

        # 15/12/2020
        journal_items_65 = [{
            'account_id': self.default_account_6415.id,
            'debit': 16000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3521.id,
            'debit': 0,
            'credit': 16000,
            'date_maturity': date(2022, 3, 31),
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_65)

        # 15/12/2020
        journal_items_66 = [{
            'account_id': self.default_account_4212.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_3561.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_66)

        # 15/12/2020
        journal_items_67 = [{
            'account_id': self.default_account_3432.id,
            'debit': 1000000,
            'credit': 0,
            'date_maturity': date(2022, 6, 15),
        },
        {
            'account_id': self.default_account_4113.id,
            'debit': 0,
            'credit': 1000000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_67)

        # 15/12/2020
        journal_items_68 = [{
            'account_id': self.default_account_1121.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4118.id,
            'debit': 0,
            'credit': 50000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_68)

        # 15/12/2020
        journal_items_69 = [{
            'account_id': self.default_account_419.id,
            'debit': 500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 500000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_69)

        # 31/12/2020
        journal_items_70 = [{
            'account_id': self.default_account_2111.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_412.id,
            'debit': 0,
            'credit': 50000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_70)

        # 31/12/2020
        journal_items_72 = [{
            'account_id': self.default_account_4212.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_414.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_72)

        # 15/12/2020
        journal_items_73 = [{
            'account_id': self.default_account_1385.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_417.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_73)

        # 15/12/2020
        journal_items_74 = [{
            'account_id': self.default_account_4212.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_418.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 15, 12, 0), self.default_journal_vn_misc, items=journal_items_74)

        # 01/01/2020
        journal_items_75 = [{
            'account_id': self.default_account_4212.id,
            'debit': 100000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4211.id,
            'debit': 0,
            'credit': 100000,
        }]
        self._init_journal_entry(None , datetime(2020, 1, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_75)

        # 01/01/2020
        journal_items_76 = [{
            'account_id': self.default_account_1121.id,
            'debit': 1500000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_441.id,
            'debit': 0,
            'credit': 1500000,
        }]
        self._init_journal_entry(None , datetime(2020, 1, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_76)

        # 01/01/2020
        journal_items_77 = [{
            'account_id': self.default_account_441.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_1121.id,
            'debit': 0,
            'credit': 50000,
        }]
        self._init_journal_entry(None , datetime(2020, 1, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_77)

        # 01/01/2020
        journal_items_78 = [{
            'account_id': self.default_account_1121.id,
            'debit': 50000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4612.id,
            'debit': 0,
            'credit': 50000,
        }]
        self._init_journal_entry(None , datetime(2020, 1, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_78)

        # 01/01/2020
        journal_items_79 = [{
            'account_id': self.default_account_2112.id,
            'debit': 30000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4612.id,
            'debit': 0,
            'credit': 30000,
        },
        {
            'account_id': self.default_account_1612.id,
            'debit': 30000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_466.id,
            'debit': 0,
            'credit': 30000,
        }]
        self._init_journal_entry(None , datetime(2020, 1, 1, 12, 0), self.default_journal_vn_misc, items=journal_items_79)

        # 31/12/2020
        journal_items_80 = [{
            'account_id': self.default_account_5111.id,
            'debit': 700000,
            'credit': 0,
        },
        {
            'account_id': self.default_account_911.id,
            'debit': 0,
            'credit': 700000,
        },
        {
            'account_id': self.default_account_632.id,
            'debit': 0,
            'credit': 120000,
        },
        {
            'account_id': self.default_account_635.id,
            'debit': 0,
            'credit': 12500,
        },
        {
            'account_id': self.default_account_6415.id,
            'debit': 0,
            'credit': 32000,
        },
        {
            'account_id': self.default_account_6421.id,
            'debit': 0,
            'credit': 21780,
        },
        {
            'account_id': self.default_account_6424.id,
            'debit': 0,
            'credit': 20000,
        },
        {
            'account_id': self.default_account_6426.id,
            'debit': 0,
            'credit': 230000,
        },
        {
            'account_id': self.default_account_6427.id,
            'debit': 0,
            'credit': 25000,
        },
        {
            'account_id': self.default_account_911.id,
            'debit': 461280,
            'credit': 0,
        },
        {
            'account_id': self.default_account_911.id,
            'debit': 238720,
            'credit': 0,
        },
        {
            'account_id': self.default_account_4212.id,
            'debit': 0,
            'credit': 238720,
        }]
        self._init_journal_entry(None , datetime(2020, 12, 31, 12, 0), self.default_journal_vn_misc, items=journal_items_80)
        lines = self._get_lines_report(self.AccountBalanceSheetReport, datetime(2020, 12, 31, 12, 0))
        table_value = [
            ('Total A - CURRENT ASSETS (100 = 110 + 120 + 130 + 140 + 150)', 13424500),
            ('Total I. Cash and Cash Equivalents (110 = 111 + 112)', 8647000),
            ('1. Bank & Cash', 8347000),
            ('2. Cash equivalents', 300000),
            ('Total II. Cash flows from investing activities (120 = 121 + 122 + 123)', 947500),
            ('1. Trading securities', 450000),
            ('2. Allowances for decline in value of trading securities', -2500),
            ('3. Held to maturity investments', 500000),
            ('Total III. Short-term receivables (130 = 131 + 132 + 133 + 134 + 135 + 136 + 137 + 139)', 1891000),
            ('1. Short-term trade receivables', 1540000),
            ('2. Short-term prepayments to suppliers', 5000),
            ('3. Short-term intra-company receivables', 10000),
            ('4. Receivables under schedule of construction contract', 200000),
            ('5. Short-term loan receivables', 50000),
            ('6. Other short-term receivables', 110000),
            ('7. Short-term allowances for doubtful debts', -25000),
            ('8. Shortage of assets awaiting resolution', 1000),
            ('Total IV. Inventories (140 = 141 + 149)', 1419000),
            ('Total 1. Inventories', 1524000),
            ('1.a. All Inventories', 1499000),
            ('1.b. Minus Long-term work in progress', 25000),
            ('1.c. Minus Long-term equipment and spare parts for replacement', 0),
            ('2. Allowances for decline in value of inventories', -105000),
            ('Total V. Other current assets (150 = 151 + 152 + 153 + 154 + 155)', 520000),
            ('1. Short-term prepaid expenses', 120000),
            ('2. Deductible VAT', 200000),
            ('3. Taxes and other receivables from government budget', 0),
            ('4. Government bonds purchased for resale', 0),
            ('5. Other current assets', 200000),
            ('Total B - NON-CURRENT ASSETS (200 = 210 + 220 + 240 + 250 + 260)', 10585000),
            ('Total I. Long-term receivables (210 = 211 + 212 + 213 + 214 + 215 + 216 + 219)', 1800000),
            ('1. Long-term trade receivables', 790000),
            ('2. Long-term prepayments to suppliers', 0),
            ('3. Working capital provided to sub-units', 1000000),
            ('4. Long-term intra-company receivables', 20000),
            ('5. Long-term loan receivables', 40000),
            ('Total 6. Other long-term receivables', 30000),
            ('6a. Other long-term receivables (assets)', 30000),
            ('6b. Other long-term receivables (equity)', 0),
            ('7. Long-term allowances for doubtful debts', -80000),
            ('Total II. Fixed assets (220 = 221 + 224 + 227 + 230)', 4810000),
            ('Total 1. Tangible fixed assets (221 = 222 + 223)', 1240000),
            ('- Historical costs', 1250000),
            ('- Accumulated depreciation', -10000),
            ('Total 2. Finance lease fixed assets (224 = 225 + 226)', 1190000),
            ('- Historical costs', 1200000),
            ('- Accumulated depreciation', -10000),
            ('Total 3. Intangible fixed assets (227 = 228 + 229)', 1190000),
            ('- Historical costs', 1200000),
            ('- Accumulated depreciation', -10000),
            ('Total III. Investment properties (230 = 231 + 232)', 1190000),
            ('- Historical costs', 1200000),
            ('- Accumulated depreciation', -10000),
            ('Total IV. Long-term assets in progress (240 = 241 + 242)', 20000),
            ('1. Long-term work in progress', -25000),
            ('2. Construction in progress', 45000),
            ('Total V. Long-term investments (250 = 251 + 252 + 253 + 254 + 255)', 3480000),
            ('1. Investments in subsidiaries', 1000000),
            ('2. Investments in joint ventures and associates', 1000000),
            ('3. Investments in equity of other entities', 1000000),
            ('4. Allowances for long-term investments', -20000),
            ('5. Held to maturity investments', 500000),
            ('Total VI. Other long-term assets (260 = 261 + 262 + 263 + 268)', 475000),
            ('1. Long-term prepaid expenses', 360000),
            ('2. Deferred income tax assets', 15000),
            ('3. Long-term equipment and spare parts for replacement', 0),
            ('4. Other long-term assets', 100000),
            ('TOTAL ASSETS (270 = 100 + 200)', 24009500),
            ('Total C - LIABILITIES (300 = 310 + 330)', 15235780),
            ('Total I. Short-term liabilities (310 = 311 + 312 + 313 + 314 + 315 + 316 + 317 + 318 + 319 + 320 + 321 + 322 + 323 + 324)', 2982780),
            ('1. Short-term trade payables', 540000),
            ('2. Short-term prepayments from customers', 550000),
            ('3. Taxes and other payables to government budget', 150000),
            ('4. Payables to employees', 18000),
            ('5. Short-term accrued expenses', 5000),
            ('6. Short-term intra-company payables', 10000),
            ('7. Payables under schedule of construction contract', 200000),
            ('8. Short-term unearned revenues', 240000),
            ('9. Other short-term payments', 3780),
            ('10. Short-term borrowings and finance lease liabilities', 1000000),
            ('11. Short-term provisions', 16000),
            ('12. Bonus and welfare fund', 100000),
            ('13. Price stabilization fund', 100000),
            ('14. Government bonds purchased for resale', 50000),
            ('Total II. Long-term liabilities (330 = 331 + 332 + 333 + 334 + 335 + 336 + 337 + 338 + 339 + 340 + 341 + 342 + 343)', 12253000),
            ('1. Long-term trade payables', 560000),
            ('2. Long-term prepayments from customers', 0),
            ('3. Long-term accrued expenses', 10000),
            ('4. Intra-company payables for operating capital received', 1000000),
            ('5. Long-term intra-company payables', 10000),
            ('6. Long-term unearned revenues', 240000),
            ('7. Other long-term payables', 2000),
            ('8. Long-term borrowings and finance lease liabilities', 10000000),
            ('9. Convertible bonds', 0),
            ('10. Preference shares', 300000),
            ('11. Deferred income tax payables', 15000),
            ('12. Long-term provisions', 16000),
            ('13. Science and technology development fund', 100000),
            ('Total D - OWNER’S EQUITY (400 = 410 + 430)', 9068720),
            ('Total I. Owner’s equity (410 = 411 + 412 + 413 + 414 + 415 + 416 + 417 + 418 + 419 + 420 + 421 + 422)', 8988720),
            ('Total 1. Contributed capital', 6000000),
            (' - Ordinary shares with voting rights', 700000),
            (' - Preference shares', 300000),
            ('2. Capital surplus', 300000),
            ('3. Conversion options on convertible bonds', 1000000),
            ('4. Other capital', 50000),
            ('5. Treasury shares', -500000),
            ('6. Differences upon asset revaluation', 50000),
            ('7. Exchange rate differences', 0),
            ('8. Development and investment funds', 100000),
            ('9. Enterprise reorganization assistance fund', 100000),
            ('10. Other equity funds', 100000),
            ('Total 11. Undistributed profit after tax', 338720),
            ('- Undistributed profit after tax brought forward', 100000),
            ('- Undistributed profit after tax for the current year', 238720),
            ('12. Capital expenditure funds', 1450000),
            ('Total II. Funding sources and other funds (430 = 431 + 432)', 80000),
            ('1. Funding sources', 50000),
            ('2. Funds used for fixed asset acquisition', 30000),
            ('TOTAL EQUITY (440 = 300 + 400)',24304500),
        ]
        self._check_report_value(lines, table_value)
