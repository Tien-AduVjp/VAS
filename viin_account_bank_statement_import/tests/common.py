# -*- coding: utf-8 -*-
import base64

from odoo.addons.account.tests.test_account_bank_statement import TestAccountBankStatementCommon
from odoo.modules.module import get_module_resource


class BankStatementImportCommon(TestAccountBankStatementCommon):
    """ Tests for import bank statement in CSV format"""

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.partner_bank_account_a = cls.env['res.partner.bank'].create({
            'acc_number': 'BE32707171912448',
            'partner_id': cls.partner_a.id,
            'acc_type': 'bank',
        })
        cls.partner_bank_account_b = cls.env['res.partner.bank'].create({
            'acc_number': 'BE32707171912449',
            'partner_id': cls.partner_b.id,
            'acc_type': 'bank',
        })

    def _read_bank_statement_file(self, *rel_path):
        """
        Read bank statement file from disk
        @param rel_path: component paths, e.g. 'viin_account_bank_statement_import', 'static', 'samples', 'Import_Sample.csv'
        """
        abs_file_path = get_module_resource(*rel_path)
        with open(abs_file_path, 'rb') as f:
            return base64.b64encode(f.read())

