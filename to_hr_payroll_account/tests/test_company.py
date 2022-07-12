from odoo import fields
from odoo.tests import tagged
from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestCompany(TestCommon):
    def test_company(self):
        """
        Case 2: Test Sổ nhật ký trên Hợp đồng
            Input: Tất cả Hợp đồng
            Output: sổ nhật ký trên hợp đồng là sổ nhật ký "Lương nhân viên", mã "SAL"
        """
        chart_template = self.env['account.chart.template'].search([], limit=1)
        company = self.env['res.company'].create({
            'name': 'company test',
            'chart_template_id': chart_template.id
        })
        self.env.company = company
        employee = self.create_employee('Employee test')
        employee.write({
            'company_id': company.id
            })
        contract = self.create_contract(
            employee.id,
            fields.Date.from_string('2021-1-1'),
            fields.Date.from_string('2021-12-31'))
        contract.write({
            'company_id': company.id
            })
        payslip = self.create_payslip(
            employee.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            contract.id)
        journal = self.env['account.journal'].search([], limit = 1)
        batch = self.env['hr.payslip.run'].create({
            'name': 'Test 1',
            'date_start': fields.Date.from_string('2021-7-1'),
            'date_end': fields.Date.from_string('2021-7-31'),
            'salary_cycle_id': company.salary_cycle_id.id,
            'journal_id': journal.id,
            'company_id': company.id
        })

        company._generate_salary_account_journals()
        company._fill_journal_to_payslips()

        journal = self.env['account.journal'].search([
                ('company_id', '=', company.id),
                ('code', '=', 'SAL')
                ], limit = 1)
        self.assertTrue(journal, 'test _generate_salary_account_journals() not oke')
        self.assertEqual(journal, contract.journal_id, 'test _fill_journal_to_payslips() not oke')
        self.assertEqual(journal, payslip.journal_id, 'test _fill_journal_to_payslips() not oke')
        self.assertEqual(journal, batch.journal_id, 'test _fill_journal_to_payslips() not oke')
