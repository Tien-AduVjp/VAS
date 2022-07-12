# -*- coding: utf-8 -*-
import base64

from odoo.tests.common import TransactionCase
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError


class TestRJEFile(TransactionCase):
    """ Tests for import bank statement rje file format (account.bank.statement.import) """

    def test_rje_file_import(self):
        # activate VND
        self.env.ref("base.VND").write({'active': True})

        # Create a bank account and journal corresponding to the RJE file (same currency and account number)
        bank_journal = self.env['account.journal'].create({
            'name': 'Bank 1234567890',
            'code': 'BNK67',
            'type': 'bank',
            'bank_acc_number': '1234567890',
            'currency_id': self.env.ref("base.VND").id
            })

        # import 1 file with wrong name
        jre_file_path = get_module_resource('to_account_bank_statement_import_rje', 'static', 'rje', 'test_rje.JRE')
        jre_file = base64.b64encode(open(jre_file_path, 'rb').read())
        with self.assertRaises(UserError):
            import_wizard = self.env['account.bank.statement.import'].with_context(journal_id=bank_journal.id).create({
                'attachment_ids': [
                    (0, 0, {
                        'name': 'test_rje.JRE',
                        'datas': jre_file,
                        })
                    ],
                })
            import_wizard.import_file()

        # import 1 file with wrong content
        rje_blank_file_path = get_module_resource('to_account_bank_statement_import_rje', 'static', 'rje', 'test_rje_blank.RJE')
        rje_blank_file = base64.b64encode(open(rje_blank_file_path, 'rb').read())
        with self.assertRaises(UserError):
            import_wizard = self.env['account.bank.statement.import'].with_context(journal_id=bank_journal.id).create({
                'attachment_ids': [
                    (0, 0, {
                        'name': 'test_rje_blank.RJE',
                        'datas': rje_blank_file,
                        })
                    ],
                })
            import_wizard.import_file()
       
        # Get RJE file content
        rje_file_path = get_module_resource('to_account_bank_statement_import_rje', 'static', 'rje', 'test_rje.RJE')
        rje_file = base64.b64encode(open(rje_file_path, 'rb').read())

        # Use an import wizard to process the file
        import_wizard = self.env['account.bank.statement.import'].with_context(journal_id=bank_journal.id).create({
            'attachment_ids': [
                (0, 0, {
                    'name': 'test_rje.RJE',
                    'datas': rje_file,
                    })
                ],
            })
        import_wizard.import_file()

        # Check the imported bank statement
        bank_st_record = self.env['account.bank.statement'].search([('reference', '=', 'test_rje.RJE')], limit=1)
        self.assertEqual(bank_st_record.balance_start, 0.0)
        self.assertEqual(bank_st_record.balance_end_real, 158981994.00)

        # Check an imported bank statement line
        line = bank_st_record.line_ids.filtered(lambda r: r.ref == 'NONREF2500')
        self.assertEqual(line.date.strftime('%d/%m/%Y'), '06/12/2019')
        self.assertEqual(line.amount, 1000000)
        self.assertEqual(line.name, 'IB NGUYEN THI LIEN NOP TU TM')
