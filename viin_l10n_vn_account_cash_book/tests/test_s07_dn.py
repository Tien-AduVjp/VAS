import xlrd

from datetime import date
from odoo.tests import Form, TransactionCase


class TestS07Dn(TransactionCase):
    def setUp(self):
        super(TestS07Dn, self).setUp()

        self.account_1112 = self.env['account.account'].create({
            'name': 'Ngoại tệ',
            'code': 111001,
            'user_type_id': self.env.ref('account.data_account_type_liquidity').id
        })

        self.entry = self.env['account.move'].create({
            'line_ids': [
                (0, 0, {
                    'account_id': self.account_1112.id,
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

    def test_s07_dn(self):
        self.entry.post()
        l10n_vn_c200_s07dn = Form(self.env['wizard.l10n_vn.c200.s07dn']).save()
        byte_date = l10n_vn_c200_s07dn.report_excel().getvalue()
        workbook = xlrd.open_workbook(file_contents=byte_date)
        worksheet = workbook.sheet_by_index(0)
        today = date.today().strftime('%m/%d/%Y')
        self.assertEqual(worksheet.cell_value(12, 0), today)
        self.assertEqual(worksheet.cell_value(12, 1), today)
        self.assertEqual(worksheet.cell_value(12, 6), 100000.0)
        self.assertEqual(worksheet.cell_value(12, 7), 0.0)
        self.assertEqual(worksheet.cell_value(12, 8), 100000.0)

        self.assertEqual(worksheet.cell_value(13, 6), 100000.0)
        self.assertEqual(worksheet.cell_value(13, 7), 0.0)
        self.assertEqual(worksheet.cell_value(13, 8), 0.0)

        self.assertEqual(worksheet.cell_value(14, 8), 100000.0)
