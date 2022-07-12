# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import tagged
from odoo.exceptions import UserError
from odoo.addons.viin_account_bank_statement_import.tests.common import BankStatementImportCommon


@tagged('post_install', '-at_install')
class TestImportRJE(BankStatementImportCommon):
    """ Tests for import bank statement rje file format (account.bank.statement.import) """

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env.ref('base.VND').write({'active': True})
        cls.vnd_bank_journal = cls.env['account.journal'].create({
            'name': 'Bank 1234567890',
            'code': 'BNK67',
            'type': 'bank',
            'bank_acc_number': '1234567890',
            'currency_id': cls.env.ref('base.VND').id
            })
        cls.vnd_rate = cls.env['res.currency.rate'].create({
            'name': '2019-12-06',
            'rate': 2,
            'currency_id': cls.env.ref('base.VND').id,
            'company_id': cls.env.company.id,
        })

    def test_01_invalid_rje_file_extension(self):
        jre_file = self._read_bank_statement_file('viin_account_bank_statement_import_rje', 'static', 'rje', 'test_rje.JRE')
        with self.assertRaises(UserError):
            import_wizard = self.env['account.bank.statement.import'].with_context(
                journal_id=self.vnd_bank_journal.id
                ).create({
                    'attachment_ids': [
                        (0, 0, {
                            'name': 'test_rje.JRE',
                            'datas': jre_file,
                            })
                        ],
                    })
            import_wizard.import_file()

    def test_11_invalid_rje_file_content(self):
        rje_blank_file = self._read_bank_statement_file('viin_account_bank_statement_import_rje', 'static', 'rje', 'test_rje_blank.RJE')
        with self.assertRaises(UserError):
            import_wizard = self.env['account.bank.statement.import'].with_context(
                journal_id=self.vnd_bank_journal.id
                ).create({
                    'attachment_ids': [
                        (0, 0, {
                            'name': 'test_rje_blank.RJE',
                            'datas': rje_blank_file,
                            })
                        ],
                    })
            import_wizard.import_file()

    def test_22_rje_file_import_wrong_currency(self):
        """
        Import RJE with VND into a USD journal that is expected to raise UserError
        """
        rje_file = self._read_bank_statement_file('viin_account_bank_statement_import_rje', 'static', 'rje', 'test_rje.RJE')
        # Use an import wizard to process the file
        import_wizard = self.env['account.bank.statement.import'].with_context(
            journal_id=self.bank_journal_1.id  # USD journal
            ).create({
                'attachment_ids': [
                    (0, 0, {
                        'name': 'test_rje.RJE',
                        'datas': rje_file,
                        })
                    ],
                })
        with self.assertRaises(UserError):
            import_wizard.import_file()

    def test_22_rje_file_import(self):
        rje_file = self._read_bank_statement_file('viin_account_bank_statement_import_rje', 'static', 'rje', 'test_rje.RJE')
        # Use an import wizard to process the file
        import_wizard = self.env['account.bank.statement.import'].with_context(
            journal_id=self.vnd_bank_journal.id
            ).create({
                'attachment_ids': [
                    (0, 0, {
                        'name': 'test_rje.RJE',
                        'datas': rje_file,
                        })
                    ],
                })
        import_wizard.import_file()

        bank_st_record = self.env['account.bank.statement'].search([('reference', '=', 'test_rje.RJE')], limit=1)
        # assert statement values
        self.assertRecordValues(
            bank_st_record,
            [
                {
                    'balance_start': 0.0,
                    'balance_end': 158981994.0,
                    'balance_end_real': 158981994.0,
                    'currency_id': self.env.ref('base.VND').id,
                    'date': date(2019, 12, 31),
                    'difference': 0.0,
                    'is_valid_balance_start': True,
                    'journal_id': self.vnd_bank_journal.id,
                    'state': 'open',  # RJE sample has no partner specified. Hence, it should be in open state
                    }
                ]
            )
        # assert statement lines
        lines = bank_st_record.line_ids
        # assert lines count
        self.assertTrue(len(lines) == 31, "It's OK to have 31 lines generated from test_rje.RJE")
        # assert one of the statement lines
        NONREF2500_line = lines.filtered(lambda r: r.ref == 'NONREF2500')
        self.assertTrue(len(NONREF2500_line) == 1, "NONREF2500_line found.")
        self.assertRecordValues(
            NONREF2500_line,
            [
                {
                    'date': date(2019, 12, 6),
                    'amount': 1000000.0,
                    'payment_ref': 'IB NGUYEN THI LIEN NOP TU TM'
                    }
                ]
            )

        # post the statement to have account moves generated
        bank_st_record.button_post()
        # if statement is posted, it should have name
        self.assertEqual(bank_st_record.name, 'BNK67 Statement 2019/12/00001')
        # if statement is posted, it should have account moves
        self.assertTrue(len(lines.move_id) == 31, "It's OK to have 31 journal entries generated from test_rje.RJE")
        with self.env.cr.savepoint():
            self.assertRecordValues(
                NONREF2500_line.move_id,
                [
                    {
                        'name': 'BNK67/2019/12/0001',
                        'date': date(2019, 12, 6),
                        'amount_total': 1000000.0,
                        'narration': 'IB NGUYEN THI LIEN NOP TU TM',
                        'journal_id': self.vnd_bank_journal.id,
                        'currency_id': self.env.ref('base.VND').id,
                        }
                    ]
                )
            self.assertRecordValues(
                NONREF2500_line.move_id.line_ids,
                [
                    {
                        'name': 'IB NGUYEN THI LIEN NOP TU TM',
                        'date': date(2019, 12, 6),
                        'amount_currency': 1000000.0,
                        'debit': 500000.0,
                        'credit': 0.0,
                        'journal_id': self.vnd_bank_journal.id,
                        'currency_id': self.env.ref('base.VND').id,
                        },
                    {
                        'name': 'IB NGUYEN THI LIEN NOP TU TM',
                        'date': date(2019, 12, 6),
                        'amount_currency':-1000000.0,
                        'debit': 0.0,
                        'credit': 500000.0,
                        'journal_id': self.vnd_bank_journal.id,
                        'currency_id': self.env.ref('base.VND').id,
                        }
                    ]
                )

