import xlrd
from datetime import date, datetime
from odoo.tests import Form
from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class TestS08Dn(Common):

    def setUp(self):
        super(TestS08Dn, self).setUp()

        journal_items_1 = [{
            'account_id': self.default_account_1121.id,
            'debit': 100000,
            'credit': 0.0
        },
        {
            'account_id': self.default_account_131.id,
            'debit': 0.0,
            'credit': 100000
        }]
        journal_entry_1 = self._init_journal_entry(None , datetime.now(), self.default_journal_vn_misc, items=journal_items_1)

    def test_s08_dn(self):
        l10n_vn_c200_s08dn = Form(self.env['l10n_vn.s08dn']).save()
        byte_date = l10n_vn_c200_s08dn.report_excel().getvalue()
        workbook = xlrd.open_workbook(file_contents=byte_date)
        worksheet = workbook.sheet_by_index(0)
        today = date.today().strftime('%m/%d/%Y')
        self.assertEqual(worksheet.cell_value(14, 0), today)
        self.assertEqual(worksheet.cell_value(14, 2), today)
        self.assertEqual(worksheet.cell_value(14, 5), 100000)
        self.assertEqual(worksheet.cell_value(14, 6), 0.0)
        self.assertEqual(worksheet.cell_value(14, 7), 100000)

        self.assertEqual(worksheet.cell_value(15, 5), 100000)
        self.assertEqual(worksheet.cell_value(15, 6), 0)
        self.assertEqual(worksheet.cell_value(15, 7), 0)

        self.assertEqual(worksheet.cell_value(16, 7), 100000)
