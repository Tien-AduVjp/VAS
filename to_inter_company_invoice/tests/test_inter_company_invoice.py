from odoo import _
from odoo.exceptions import AccessError
from odoo.tests import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestInterCompanyInvoice(SavepointCase):

    def setUp(self):
        super(TestInterCompanyInvoice, self).setUp()

        self.chart_template = self.env.ref(
            'l10n_generic_coa.configurable_chart_template', raise_if_not_found=False)
        self.product_test_01 = self.env['product.product'].create({
            'name': 'Viin Product Test 01',
            'type': 'product'
        })
        self.customer_company = self.env['res.company'].create({
            'name': 'Customer Company',
            'currency_id': self.ref('base.USD')
        })
        self.vendor_company = self.env['res.company'].create({
            'name': "Vendor Company",
            'currency_id': self.ref('base.USD')
        })
        self.chart_template.try_loading(company=self.vendor_company)
        self.chart_template.try_loading(company=self.customer_company)
        self.account_revenue = self.env['account.account'].create({
            'code': '99880001',
            'name': 'Product Sale -Test',
            'user_type_id': self.ref('account.data_account_type_revenue'),
            'company_id': self.vendor_company.id
        })
        self.account_expense = self.env['account.account'].create({
            'code': '99880002',
            'name': 'Expenses-Test',
            'user_type_id': self.ref('account.data_account_type_expenses'),
            'company_id': self.customer_company.id
        })
        self.journal_vendor_company = self.env['account.journal'].create({
            'name': 'Vendor Invoice',
            'type': 'sale',
            'code': 'INV_TS',
            'company_id': self.vendor_company.id
        })
        self.journal_customer_company = self.env['account.journal'].create({
            'name': 'Customer Bill',
            'type': 'purchase',
            'code': 'BIL_TS',
            'company_id': self.customer_company.id
        })
        self.user_vendor, self.user_customer, self.user_inter_company_customer,self.user_inter_company_vendor = self.env['res.users'].create([
            {
                'name':'User Vendor Bot',
                'login':'user_vendor_bot',
                'email':'user.vendor.bot@vendor.com',
                'groups_id':[(6,0,[self.env.ref('account.group_account_invoice').id])],
                'in_group_4':True,
                'company_id':self.vendor_company.id,
                'company_ids':[(6,0,[self.vendor_company.id,self.customer_company.id])]
            },
            {
                'name':'User Customer Bot',
                'login':'user_customer_bot',
                'email':'user.customer.bot@customer.com',
                'groups_id':[(6,0,[self.env.ref('account.group_account_invoice').id])],
                'in_group_4':True,
                'company_id':self.vendor_company.id,
                'company_ids':[(6,0,[self.vendor_company.id,self.customer_company.id])]
            },
            {
                'name':'User Inter-Company Customer Bot',
                'login':'inter_customer_bot',
                'email':'inter_customer_user@company.com',
                'in_group_4':True,
                'company_id':self.customer_company.id,
                'company_ids':[(6,0,[self.vendor_company.id,self.customer_company.id])]
            },
            {
                'name':'User Inter-Company Vendor Bot',
                'login':'inter_vendor_bot',
                'email':'inter_vendor_user@company.com',
                'in_group_4':True,
                'company_id':self.customer_company.id,
                'company_ids':[(6,0,[self.vendor_company.id,self.customer_company.id])]
            }
        ])
        self.context_allowed_company_ids = {'allowed_company_ids':[self.vendor_company.id, self.customer_company.id]}
        self.vendor_company.intercompany_user_id = self.user_inter_company_vendor.id
        self.customer_company.intercompany_user_id = self.user_inter_company_customer.id

    def _generate_account_move(self, partner_id, company_id, move_type, journal_id, account_id, user = None):
        return self.env['account.move'].with_user(user).create({
            'partner_id': partner_id,
            'move_type': move_type,
            'company_id': company_id,
            'journal_id': journal_id,
            'currency_id': self.ref('base.USD'),
            'invoice_date':"2022-01-01",
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_test_01.id,
                'quantity': 1,
                'price_unit': 100.0,
                'currency_id': self.ref('base.USD'),
                'account_id': account_id
            })]
        })

    def _is_send_message_when_cancel_invoice(self, invoice):
        invoice.button_cancel()
        message = _("The inter-company invoice %s of the company %s was cancelled. Please contact that company to solve the issue.")\
            % (invoice.name, invoice.company_id.name)
        return invoice.inter_comp_invoice_id.message_ids.filtered(lambda m: message in m.body) and True

    def test_01a_auto_generate_inter_company_purchase_invoice(self):
        """
            Case: Test generate inter-company purchase invoice in case Inter-Company User of customer company in group account invoice.
            Expect: When create and post sale invoice in vendor company, purchase invoice will auto generate in customer company.
        """
        self.user_inter_company_customer.groups_id = [(6,0,[self.env.ref('account.group_account_invoice').id])]
        self.account_move_sale_test_01 = self._generate_account_move(
            partner_id=self.customer_company.partner_id.id,
            move_type='out_invoice',
            company_id=self.vendor_company.id,
            journal_id=self.journal_vendor_company.id,
            account_id=self.account_revenue.id,
            user=self.user_vendor
        )
        self.account_move_sale_test_01.with_context(self.context_allowed_company_ids).with_user(self.user_vendor).action_post()
        inter_comp_customer_invoice = self.env['account.move'].search(
            [
                ('company_id', '=', self.customer_company.id),
                ('inter_comp_invoice_id', '=', self.account_move_sale_test_01.id)
            ])
        self.assertTrue(len(inter_comp_customer_invoice) == 1 and inter_comp_customer_invoice.move_type == 'in_invoice',
                        "Purchase Invoice should be created correlative with Sale Invoice")
        # a message should be sent to inter-company if invoice was canceled
        self.assertTrue(self._is_send_message_when_cancel_invoice(
            self.account_move_sale_test_01))

    def test_01b_auto_generate_inter_company_purchase_invoice(self):
        """
            Case: Test generate inter-company purchase invoice in case Inter-Company User of customer company NOT IN group account invoice.
            Expect: When and post sale invoice in vendor company will show access right error.
        """
        self.account_move_sale_test_01 = self._generate_account_move(
            partner_id=self.customer_company.partner_id.id,
            move_type='out_invoice',
            company_id=self.vendor_company.id,
            journal_id=self.journal_vendor_company.id,
            account_id=self.account_revenue.id,
            user=self.user_vendor
        )
        with self.assertRaises(AccessError):
            self.account_move_sale_test_01.with_context(self.context_allowed_company_ids).with_user(self.user_vendor).action_post()

    def test_02a_auto_generate_inter_company_sale_invoice(self):
        """
            Case: Test generate inter company sale invoice incase Inter-Company User of vendor company in group account invoice.
            Expect: When create and post purchase invoice in customer company, sale invoice will auto generate in vendor company.
        """
        self.user_inter_company_vendor.groups_id = [(6,0,[self.env.ref('account.group_account_invoice').id])]
        self.account_move_purchase_test_01 = self._generate_account_move(
            partner_id=self.vendor_company.partner_id.id,
            move_type='in_invoice',
            company_id=self.customer_company.id,
            journal_id=self.journal_customer_company.id,
            account_id=self.account_expense.id,
            user = self.user_customer
        )
        self.account_move_purchase_test_01.with_context(self.context_allowed_company_ids).with_user(self.user_customer).action_post()
        inter_comp_vendor_invoice = self.env['account.move'].search([
            ('company_id', '=', self.vendor_company.id),
            ('inter_comp_invoice_id', '=', self.account_move_purchase_test_01.id)
        ])
        self.assertTrue(len(inter_comp_vendor_invoice) == 1 and inter_comp_vendor_invoice.move_type == 'out_invoice',
                        "Sale Invoice should be created correlative with Purchase Invoice")
        # a message should be sent to inter-company if invoice was canceled
        self.assertTrue(self._is_send_message_when_cancel_invoice(
            self.account_move_purchase_test_01))

    def test_02b_auto_generate_inter_company_sale_invoicetest_02(self):
        """
            Case: Test generate inter-company sale invoice in case Inter-Company User of vendor company NOT IN group account invoice.
            Expect: When post purchase invoice in vendor company will show access right error of inter-company user.
        """
        self.account_move_purchase_test_01 = self._generate_account_move(
            partner_id=self.vendor_company.partner_id.id,
            move_type='in_invoice',
            company_id=self.customer_company.id,
            journal_id=self.journal_customer_company.id,
            account_id=self.account_expense.id,
            user = self.user_customer
        )
        with self.assertRaises(AccessError):
            self.account_move_purchase_test_01.with_context(self.context_allowed_company_ids).with_user(self.user_customer).action_post()

    def test_03a_auto_generate_inter_company_credit_note_invoice(self):
        """
            Case: Test generate inter-company credit note invoice in case Inter-Company User of vendor company in group account invoice.
            Expect: When create and post refund invoice in vendor company, credit note invoice will auto generate in vendor company.
        """
        self.user_inter_company_vendor.groups_id = [(6,0,[self.env.ref('account.group_account_invoice').id])]
        self.account_move_refund_test_01 = self._generate_account_move(
            partner_id=self.vendor_company.partner_id.id,
            move_type='in_refund',
            company_id=self.customer_company.id,
            journal_id=self.journal_customer_company.id,
            account_id=self.account_expense.id,
            user = self.user_customer
        )
        self.account_move_refund_test_01.with_context(self.context_allowed_company_ids).with_user(self.user_customer).action_post()
        inter_comp_vendor_credit_note_invoice = self.env['account.move'].search([
            ('company_id', '=', self.vendor_company.id),
            ('inter_comp_invoice_id', '=', self.account_move_refund_test_01.id)
        ])
        self.assertTrue(len(inter_comp_vendor_credit_note_invoice) == 1 and inter_comp_vendor_credit_note_invoice.move_type == 'out_refund',
                        "Credit Note Invoice should be created correlative with Refund Invoice")
        # a message should be sent to inter-company if invoice was canceled
        self.assertTrue(self._is_send_message_when_cancel_invoice(
            self.account_move_refund_test_01))

    def test_03b_auto_generate_inter_company_credit_note_invoice(self):
        """
            Case: Test generate inter-company credit note invoice in case Inter-Company User of vendor company NOT IN group account invoice.
            Expect: When post refund invoice in customer company will show access right error.
        """
        self.account_move_refund_test_01 = self._generate_account_move(
            partner_id=self.vendor_company.partner_id.id,
            move_type='in_refund',
            company_id=self.customer_company.id,
            journal_id=self.journal_customer_company.id,
            account_id=self.account_expense.id,
            user = self.user_customer
        )
        with self.assertRaises(AccessError):
            self.account_move_refund_test_01.with_context(self.context_allowed_company_ids).with_user(self.user_customer).action_post()

    def test_04a_auto_generate_inter_company_refund_invoice(self):
        """
            Case: Test generate inter-company refund invoice in case Inter-Company User of customer company in group account invoice.
            Expect: When create and post credit note invoice in vendor company, a refund invoice will auto generate in customer company.
        """
        self.user_inter_company_customer.groups_id = [(6,0,[self.env.ref('account.group_account_invoice').id])]
        self.account_move_credit_test_01 = self._generate_account_move(
            partner_id=self.customer_company.partner_id.id,
            move_type='out_refund',
            company_id=self.vendor_company.id,
            journal_id=self.journal_vendor_company.id,
            account_id=self.account_revenue.id,
            user = self.user_vendor
        )
        self.account_move_credit_test_01.with_context(self.context_allowed_company_ids).with_user(self.user_vendor).action_post()
        inter_comp_vendor_refund_invoice = self.env['account.move'].search([
            ('company_id', '=', self.customer_company.id),
            ('inter_comp_invoice_id', '=', self.account_move_credit_test_01.id)
        ])
        self.assertTrue(len(inter_comp_vendor_refund_invoice) == 1 and inter_comp_vendor_refund_invoice.move_type == 'in_refund',
                        "Refund Invoice should be created correlative with Credit Note Invoice")
        # a message should be sent to inter-company if invoice was canceled
        self.assertTrue(self._is_send_message_when_cancel_invoice(
            self.account_move_credit_test_01))

    def test_04b_auto_generate_inter_company_refund_invoice(self):
        """
            Case: Test generate inter-company refund invoice in case Inter-Company User of customer company NOT IN group account invoice.
            Expect: When post credit note invoice in vendor company will show access right error.
        """
        self.account_move_credit_test_01 = self._generate_account_move(
            partner_id=self.customer_company.partner_id.id,
            move_type='out_refund',
            company_id=self.vendor_company.id,
            journal_id=self.journal_vendor_company.id,
            account_id=self.account_revenue.id,
            user = self.user_vendor
        )
        with self.assertRaises(AccessError):
            self.account_move_credit_test_01.with_context(self.context_allowed_company_ids).with_user(self.user_vendor).action_post()
