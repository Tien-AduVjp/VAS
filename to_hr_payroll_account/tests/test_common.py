from odoo import fields

from odoo.addons.to_hr_payroll.tests.common import TestPayrollCommon


class TestCommon(TestPayrollCommon):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        # Set default company
        cls.env.company.write({
            'payslip_batch_journal_entry': False
            })

        # Set default some rules
        cls.accounts_1 = 1
        Account = cls.env['account.account']
        # account: receivable
        cls.account_type_receivable = cls.env.ref('account.data_account_type_receivable')
        cls.account_receivable = Account.search([
            ('user_type_id', '=', cls.account_type_receivable.id),
            ('company_id', '=', cls.env.company.id)
            ], limit=1)

        # account: payable
        cls.account_type_payable = cls.env.ref('account.data_account_type_payable')
        cls.account_payable = Account.search([
            ('user_type_id', '=', cls.account_type_payable.id),
            ('company_id', '=', cls.env.company.id)
            ], limit=1)

        cls.rules_generate_account = cls.env['hr.salary.rule'].search([
            ('company_id', '=', cls.env.company.id),
            ('code', 'in', ['BASIC', 'GROSS', 'NET'])
            ])

        cls.rules_generate_account.write({
            'generate_account_move_line': True,
            'account_debit': cls.account_payable.id,
            'account_credit': cls.account_receivable.id
            })

        cls.contract_open_manager = cls.create_contract(
            cls.product_dep_manager.id,
            fields.Date.from_string('2021-1-1'),
            fields.Date.from_string('2021-12-31'),
            'open'
            )

    def create_payslip_run(self, name='', start=False, end=False):
        return self.env['hr.payslip.run'].create({
            'name': name or 'Test 1',
            'date_start': start or fields.Date.from_string('2021-7-1'),
            'date_end': end or fields.Date.from_string('2021-7-31')
        })

    def generate_payslip_run(self, batch, employees, mode=False):
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch.id,
            'mode': mode or 'batch_period',
            'employee_ids': [(6,0, employees.ids)]
        })
        wizard.compute_sheet()

    def test_journal_after_install_module(self):
        """
        Case 1: Test sổ nhật ký "Lương nhân viên"
            Input: Truy cập menu sổ nhật ký
            Output: Có bản ghi sổ nhật ký "Lương nhân viên", mã là "SAL" tương ứng với từng công ty
        """
        companies = self.env['res.company'].search([('chart_template_id', '!=', False)])
        for company in companies:
            journal = self.env['account.journal'].search([
                ('company_id', '=', company.id),
                ('code', '=', 'SAL')
                ], limit = 1)
            self.assertTrue(journal, 'Test generate salary account journals not oke')

    def test_contract_after_install_module(self):
        """
        Case 2: Test Sổ nhật ký trên Hợp đồng
            Input: Tất cả Hợp đồng
            Output: sổ nhật ký trên hợp đồng là sổ nhật ký "Lương nhân viên", mã "SAL"
        """
        companies = self.env['res.company'].search([('chart_template_id', '!=', False)])
        for company in companies:
            journal = self.env['account.journal'].search([
                ('company_id', '=', company.id),
                ('code', '=', 'SAL')
                ], limit = 1)
            contracts = self.env['hr.contract'].search([('company_id', '=', company.id)])
            self.assertEqual(contracts.journal_id, journal, 'Test account journal on contracts not oke')

    def test_payslip_after_install_module(self):
        """
        Case 2: Test Sổ nhật ký trên Hợp đồng
            Input: Tất cả Hợp đồng
            Output: sổ nhật ký trên hợp đồng là sổ nhật ký "Lương nhân viên", mã "SAL"
        """
        companies = self.env['res.company'].search([('chart_template_id', '!=', False)])
        for company in companies:
            journal = self.env['account.journal'].search([
                ('company_id', '=', company.id),
                ('code', '=', 'SAL')
                ], limit = 1)
            payslips = self.env['hr.payslip'].search([('company_id', '=', company.id)])
            if payslips:
                self.assertEqual(payslips.journal_id, journal, 'Test account journal on payslips not oke')

    def test_batch_after_install_module(self):
        """
        Case 2: Test Sổ nhật ký trên Hợp đồng
            Input: Tất cả Hợp đồng
            Output: sổ nhật ký trên hợp đồng là sổ nhật ký "Lương nhân viên", mã "SAL"
        """
        companies = self.env['res.company'].search([('chart_template_id', '!=', False)])
        for company in companies:
            journal = self.env['account.journal'].search([
                ('company_id', '=', company.id),
                ('code', '=', 'SAL')
                ], limit = 1)
            batchs = self.env['hr.payslip.run'].search([('company_id', '=', company.id)])
            if batchs:
                self.assertEqual(batchs.journal_id, journal, 'Test account journal on batchs not oke')
