import xlrd

from datetime import date
from odoo.tests import Form, TransactionCase


class TestS08Dn(TransactionCase):
    def setUp(self):
        super(TestS08Dn, self).setUp()

        self.account_1121 = self.env['account.account'].create({
            'name': 'Bank',
            'code': 112001,
            'user_type_id': self.env.ref('account.data_account_type_liquidity').id
        })

        self.entry = self.env['account.move'].create({
            'line_ids': [
                (0, 0, {
                    'account_id': self.account_1121.id,
                    'debit': 100000,
                    'credit': 0.0
                }),
                (0, 0, {
                    'account_id': self.env.ref('l10n_vn.chart131').id,
                    'debit': 0.0,
                    'credit': 100000
                })
            ]
        })

    def test_s08_dn(self):
        self.entry.post()
        l10n_vn_c200_s08dn = Form(self.env['wizard.l10n_vn.c200.s08dn']).save()
        byte_date = l10n_vn_c200_s08dn.report_excel().getvalue()
        workbook = xlrd.open_workbook(file_contents=byte_date)
        worksheet = workbook.sheet_by_index(0)
        today = date.today().strftime('%m/%d/%Y')
        self.assertEqual(worksheet.cell_value(12, 0), today)
        self.assertEqual(worksheet.cell_value(12, 2), today)
        self.assertEqual(worksheet.cell_value(12, 5), 100000)
        self.assertEqual(worksheet.cell_value(12, 6), 0.0)
        self.assertEqual(worksheet.cell_value(12, 7), 100000)

        self.assertEqual(worksheet.cell_value(13, 5), 100000)
        self.assertEqual(worksheet.cell_value(13, 6), 0)
        self.assertEqual(worksheet.cell_value(13, 7), 0)

        self.assertEqual(worksheet.cell_value(14, 7), 100000)
