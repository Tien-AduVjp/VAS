import logging
from datetime import date
from odoo.tests.common import tagged, SavepointCase

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestGeneralLedger(SavepointCase):
    
    
    @classmethod
    def setUpClass(cls): 
        super(TestGeneralLedger, cls).setUpClass()
        
        cls.company_test = cls.env['res.company'].create({
            'name': 'Company Test',
        })
        cls.env.user.company_ids |= cls.company_test
        chart_template_vn = cls.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        if not chart_template_vn:
            _logger.warn("Test skipped because VN Chart template not found ...")
            cls.skipTest(cls, "VN Chart template not found")
        chart_template_vn.try_loading(company=cls.company_test)
        #search all accounts and journals of company
        accounts = cls.env['account.account'].search([('company_id', '=', cls.company_test.id)])
        journals = cls.env['account.journal'].search([('company_id', '=', cls.company_test.id)])
        
        cls.account_131 = accounts.filtered(lambda a: a.code == '131')[:1]
        cls.account_1121 = accounts.filtered(lambda a: a.code == '1121')[:1]
        cls.account_5111 = accounts.filtered(lambda a: a.code == '5111')[:1]
        cls.journal_bank = journals.filtered(lambda j: j.type == 'bank')[:1]
        cls.journal_customer_invoice = journals.filtered(lambda j: j.type == 'sale')[:1]
        
        cls.move1 = cls.env['account.move'].with_context(tracking_disable=True).create({
            'journal_id': cls.journal_customer_invoice.id,
            'date': date(2021, 10, 10),
            'line_ids': [(0, 0, {'account_id': cls.account_131.id, 'debit': 500.0, 'credit': 0.0, }),
                         (0, 0, {'account_id': cls.account_5111.id, 'debit': 0.0, 'credit': 500.0})]
        })
        cls.move1.post()
        cls.move2 = cls.env['account.move'].with_context(tracking_disable=True).create({
            'journal_id': cls.journal_bank.id,
            'date': date(2021, 10, 15),
            'line_ids': [(0, 0, {'account_id': cls.account_1121.id, 'debit': 500.0, 'credit': 0.0, }),
                         (0, 0, {'account_id': cls.account_131.id, 'debit': 0.0, 'credit': 500.0})]
        })
    
    @staticmethod
    def _prepare_report_form_data(date_from, date_to, target_move, journal_ids, company_id):
        return {
            'date_from': date_from,
            'date_to': date_to,
            'target_move': target_move,
            'journal_ids': [(6, 0, journal_ids)],
            'company_id': company_id
        }
        
    @staticmethod
    def _get_valid_lines_data(lines, keys):
        new_lines = []
        for line in lines:
            new_lines.append({key: line.get(key, False) for key in keys})
        return new_lines
        
    def test_01_moves_state_on_report(self):
        Wizard = self.env['wizard.l10n_vn.c200_s03adn']
        #Get only posted entries for report
        wizard1 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'posted', [self.journal_bank.id, self.journal_customer_invoice.id], self.company_test.id))
        lines = wizard1._prepare_data().get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['date', 'account_code', 'debit', 'credit'])
        expected_values = [
            {'date': date(2021, 10, 10), 'account_code': '131', 'debit': 500, 'credit': 0},
            {'date': date(2021, 10, 10), 'account_code': '5111', 'debit': 0, 'credit': 500},
        ]
        self.assertEqual(valid_lines, expected_values)
        #Get all journal entries for report
        wizard2 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'all', [self.journal_bank.id, self.journal_customer_invoice.id], self.company_test.id))
        lines = wizard2._prepare_data().get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['date', 'account_code', 'debit', 'credit'])
        expected_values = [
            {'date': date(2021, 10, 10), 'account_code': '131', 'debit': 500, 'credit': 0},
            {'date': date(2021, 10, 10), 'account_code': '5111', 'debit': 0, 'credit': 500},
            {'date': date(2021, 10, 15), 'account_code': '1121', 'debit': 500, 'credit': 0},
            {'date': date(2021, 10, 15), 'account_code': '131', 'debit': 0, 'credit': 500},
        ]
        self.assertEqual(valid_lines, expected_values)
    
    def test_02_period_on_report(self):
        Wizard = self.env['wizard.l10n_vn.c200_s03adn']
        self.move2.post()
        #report from 1/10/2021 to 14/10/2021
        wizard1 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 14), 'posted', [self.journal_bank.id, self.journal_customer_invoice.id], self.company_test.id))
        lines = wizard1._prepare_data().get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['date', 'account_code', 'debit', 'credit'])
        expected_values = [
            {'date': date(2021, 10, 10), 'account_code': '131', 'debit': 500, 'credit': 0},
            {'date': date(2021, 10, 10), 'account_code': '5111', 'debit': 0, 'credit': 500},
        ]
        self.assertEqual(valid_lines, expected_values)
        #report from 1/10/2021 to 31/10/2021
        wizard2 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'posted', [self.journal_bank.id, self.journal_customer_invoice.id], self.company_test.id))
        lines = wizard2._prepare_data().get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['date', 'account_code', 'debit', 'credit'])
        expected_values = [
            {'date': date(2021, 10, 10), 'account_code': '131', 'debit': 500, 'credit': 0},
            {'date': date(2021, 10, 10), 'account_code': '5111', 'debit': 0, 'credit': 500},
            {'date': date(2021, 10, 15), 'account_code': '1121', 'debit': 500, 'credit': 0},
            {'date': date(2021, 10, 15), 'account_code': '131', 'debit': 0, 'credit': 500},
        ]
        self.assertEqual(valid_lines, expected_values)
        
    def test_03_journals_on_report(self):
        Wizard = self.env['wizard.l10n_vn.c200_s03adn']
        self.move2.post()
        #Choose Customer Invoice Journal
        wizard1 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'posted', [self.journal_customer_invoice.id], self.company_test.id))
        lines = wizard1._prepare_data().get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['date', 'account_code', 'debit', 'credit'])
        expected_values = [
            {'date': date(2021, 10, 10), 'account_code': '131', 'debit': 500, 'credit': 0},
            {'date': date(2021, 10, 10), 'account_code': '5111', 'debit': 0, 'credit': 500},
        ]
        self.assertEqual(valid_lines, expected_values)
        #Choose Bank Journal
        wizard2 = Wizard.create(self._prepare_report_form_data(date(2021, 10, 1), date(2021, 10, 31), 'all', [self.journal_bank.id], self.company_test.id))
        lines = wizard2._prepare_data().get('lines', [])
        valid_lines = self._get_valid_lines_data(lines, ['date', 'account_code', 'debit', 'credit'])
        expected_values = [
            {'date': date(2021, 10, 15), 'account_code': '1121', 'debit': 500, 'credit': 0},
            {'date': date(2021, 10, 15), 'account_code': '131', 'debit': 0, 'credit': 500},
        ]
        self.assertEqual(valid_lines, expected_values)
