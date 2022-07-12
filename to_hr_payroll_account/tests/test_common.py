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

    def create_payslip_run(self, name='', start=False, end=False, date=False):
        return self.env['hr.payslip.run'].with_context(tracking_disable=True).create({
            'name': name or 'Test 1',
            'date_start': start or fields.Date.from_string('2021-7-1'),
            'date_end': end or fields.Date.from_string('2021-7-31'),
            'date': date,
            'salary_cycle_id': self.env.company.salary_cycle_id.id
        })

    def generate_payslip_run(self, batch, employees, mode=False):
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch.id,
            'mode': mode or 'batch_period',
            'employee_ids': [(6,0, employees.ids)]
        })
        wizard.compute_sheet()
