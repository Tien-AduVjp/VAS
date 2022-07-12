from odoo.tests import tagged

from odoo.addons.to_odoo_module.tests.test_common import TestCommon, odoo_module_new_user


@tagged('post_install', '-at_install')
class TestProjectTask(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestProjectTask, cls).setUpClass()

        # Create base account to simulate a chart of account
        cls.account_payable = cls.env['account.account'].create({
            'code': 'NC1110',
            'name': 'Test Payable Account',
            'user_type_id': cls.env.ref('account.data_account_type_payable').id,
            'reconcile': True
        })
        cls.account_receivable = cls.env['account.account'].create({
            'code': 'NC1111',
            'name': 'Test Receivable Account',
            'user_type_id': cls.env.ref('account.data_account_type_receivable').id,
            'reconcile': True
        })
        cls.partner.write({
            'property_account_payable_id': cls.account_payable.id,
            'property_account_receivable_id': cls.account_receivable.id,
        })

        # Set up some journals: sale
        cls.account_income = cls.env['account.account'].create({
            'code': 'NC1112',
            'name': 'Sale - Test Account',
            'user_type_id': cls.env.ref('account.data_account_type_revenue').id
        })

        cls.journal_sale = cls.env['account.journal'].create({
            'name': 'Sale Journal - Test',
            'code': 'AJ-SALE',
            'type': 'sale',
            'company_id': cls.company.id,
            'default_debit_account_id': cls.account_income.id,
            'default_credit_account_id': cls.account_income.id,
        })

        # add price for modules
        cls.test_omv_test.write({'price_currency': 13.0})

        # users
        cls.user_employee = odoo_module_new_user(cls.env, login='user_employee', groups='hr_timesheet.group_hr_timesheet_user')

        # Project and tasks
        cls.global_project = cls.env['project.project'].create({
            'name': 'Project X',
            'allow_timesheets': True,
            'partner_id': cls.partner.id,
        })

        cls.task_with_omv_no_depend = cls.env['project.task'].create({
            'name': 'Task With Odoo Module Version No Depend',
            'project_id': cls.global_project.id,
            'partner_id': cls.partner.id,
            'odoo_module_version_id': cls.test_omv_test.id
        })

        # Timesheets
        cls.timesheet_task_with_omv_no_depend = cls.env['account.analytic.line'].with_user(cls.user_employee).create({
            'name': "My timesheet 1",
            'project_id': cls.global_project.id,
            'task_id': cls.task_with_omv_no_depend.id,
            'unit_amount': 5.0,
        })

        uom_hour = cls.env.ref('uom.product_uom_hour')
        cls.product_timesheet = cls.env['product.product'].create({
            'name': "Service delivered, create a task in sales order\'s project",
            'standard_price': 10,
            'list_price': 100,
            'type': 'service',
            'invoice_policy': 'delivery',
            'uom_id': uom_hour.id,
            'uom_po_id': uom_hour.id,
            'default_code': 'SERV-DELI',
            'service_type': 'timesheet',
            'service_tracking': 'task_in_project',
            'project_id': False,
            'taxes_id': False,
        })

        cls.bank_journal = cls.env['account.journal'].create(
            {'name': 'Bank Test', 'type': 'bank', 'code': 'TBNK', 'currency_id': cls.currency.id})
        cls.payment_create_val = {
            'payment_type': 'inbound',
            'payment_method_id': cls.env.ref('account.account_payment_method_manual_in').id,
            'partner_type': 'customer',
            'partner_id': cls.partner.id,
            'currency_id': cls.currency.id,
            'journal_id': cls.bank_journal.id,
        }

    def test_download_odoo_module_version_project(self):
        wizard_create_so_from_project = self.env['project.create.sale.order'].with_context(active_id=self.global_project.id, active_model='project.project').create({
            'product_id': self.product_timesheet.id,
            'price_unit': self.product_timesheet.list_price,
            'billable_type': 'project_rate',
        })
        so_id = wizard_create_so_from_project.action_create_sale_order()['res_id']
        sale_order = self.env['sale.order'].browse(so_id)

        wizard_create_invoice_from_so = self.env['sale.advance.payment.inv'].with_context(mail_notrack=True).create({
            'advance_payment_method': 'delivered'
        })
        context = {
            'active_model': 'sale.order',
            'active_ids': [sale_order.id],
            'active_id': sale_order.id,
            'open_invoices': True
        }
        invoice_id = wizard_create_invoice_from_so.with_context(context).create_invoices()['res_id']
        invoice = self.env['account.move'].browse(invoice_id)
        invoice.post()
        amount_total = invoice.amount_total

        self.assertEqual(first=self.test_omv_test.with_context(partner=self.partner).can_download,
                         second=False,
                         msg='When the project is unpaid, the module should not be allowed to download')

        self.payment_create_val.update({
            'amount': amount_total / 2,
            'invoice_ids': [(6, 0, invoice.ids)],
        })
        payment = self.env['account.payment'].create(self.payment_create_val.copy())
        payment.post()

        self.test_omv_test.invalidate_cache()
        self.assertEqual(first=self.test_omv_test.with_context(partner=self.partner).can_download,
                         second=False,
                         msg='When the project is unpaid, the module should not be allowed to download')

        payment = self.env['account.payment'].create(self.payment_create_val.copy())
        payment.post()

        self.test_omv_test.invalidate_cache()
        self.assertEqual(first=self.test_omv_test.with_context(partner=self.partner).can_download,
                         second=True,
                         msg='When the project is paid, the module should be allowed to download')
