# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import tagged
from odoo.exceptions import UserError

from .common import BankStatementImportCommon


@tagged('post_install', '-at_install')
class TestImportCSV(BankStatementImportCommon):
    """ Tests for import bank statement in Excel xlsx format"""

    def test_01_invalid_xlsx_file_mimetype(self):
        fake_file = self._read_bank_statement_file('viin_account_bank_statement_import', 'static', 'samples', 'fake_xlsx.xlsx')
        with self.assertRaises(UserError):
            import_wizard = self.env['account.bank.statement.import'].with_context(
                journal_id=self.bank_journal_1.id
                ).create({
                    'attachment_ids': [
                        (0, 0, {
                            'name': 'fake_xlsx.xlsx',
                            'datas': fake_file,
                            })
                        ],
                    })
            import_wizard.import_file()

    def test_11_invalid_xlsx_file_content(self):
        malform_file1 = self._read_bank_statement_file('viin_account_bank_statement_import', 'static', 'samples', 'Import_Sample_malform_1.xlsx')
        with self.assertRaises(UserError):
            import_wizard = self.env['account.bank.statement.import'].with_context(
                journal_id=self.bank_journal_1.id
                ).create({
                    'attachment_ids': [
                        (0, 0, {
                            'name': 'Import_Sample_malform_1.xlsx',
                            'datas': malform_file1,
                            })
                        ],
                    })
            import_wizard.import_file()

    def test_21_xlsx_file_import(self):
        csv_file = self._read_bank_statement_file('viin_account_bank_statement_import', 'static', 'samples', 'Import_Sample.xlsx')

        # Use an import wizard to process the file
        import_wizard = self.env['account.bank.statement.import'].with_context(
            journal_id=self.bank_journal_1.id
            ).create({
                'attachment_ids': [
                    (0, 0, {
                        'name': 'Import_Sample.xlsx',
                        'datas': csv_file,
                        })
                    ],
                })
        import_wizard.import_file()

        bank_st_record = self.env['account.bank.statement'].search([('reference', '=', 'Import_Sample.xlsx')], limit=1)
        # assert statement values
        self.assertRecordValues(
            bank_st_record,
            [
                {
                    'balance_start': 0.0,
                    'balance_end': 70.0,
                    'balance_end_real': 70.0,
                    'currency_id': self.company_data['currency'].id,
                    'date': date.today(),
                    'difference': 0.0,
                    'is_valid_balance_start': True,
                    'journal_id': self.bank_journal_1.id,
                    'state': 'posted',  # the sample XLSX has partners specified for all lines so it should be posted.
                    }
                ]
            )
        # assert lines counts
        lines = bank_st_record.line_ids
        self.assertTrue(len(lines) == 2, "It's OK to have 2 lines generated from Import_Sample.xlsx")

        # assert statement lines
        self.assertRecordValues(
            lines,
            [
                {
                    'date': date(2020, 12, 1),
                    'payment_ref': 'Test 1',
                    'partner_name': 'partner_a',
                    'partner_id': self.partner_a.id,  # auto partner recognition
                    'ref': 'Ref 1',
                    'narration': '',
                    'amount': 30.0,
                    'account_number': 'BE32707171912448',
                    'partner_bank_id': self.partner_bank_account_a.id,  # auto bank recognition
                    },
                {
                    'date': date(2020, 12, 3),
                    'payment_ref': 'Test 2',
                    'partner_name': 'partner_b',
                    'partner_id': self.partner_b.id,  # auto partner recognition
                    'ref': 'Ref 2',
                    'narration': '',
                    'amount': 40.0,
                    'account_number': 'NE987654322',
                    'partner_bank_id': self.env['res.partner.bank'],  # bank does not exist

                    }
                ]
            )

        # assert account moves
        self.assertTrue(len(lines.move_id) == 2, "It's OK to have 2 journal entries generated from Import_Sample.csv")
        self.assertRecordValues(
            lines.move_id,
            [
                {
                    'name': 'BNK1/2020/12/0001',
                    'date': date(2020, 12, 1),
                    'amount_total': 30.0,
                    'narration': '',
                    'journal_id': self.bank_journal_1.id,
                    'partner_id': self.partner_a.id,
                    },
                {
                    'name': 'BNK1/2020/12/0002',
                    'date': date(2020, 12, 3),
                    'amount_total': 40.0,
                    'narration': '',
                    'journal_id': self.bank_journal_1.id,
                    'partner_id': self.partner_b.id,
                    }
                ]
            )
