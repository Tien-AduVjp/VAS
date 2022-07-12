from odoo.tests import SavepointCase, tagged, Form


@tagged('post_install', '-at_install')
class TestAccount(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(SavepointCase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref('base.res_partner_1')
        cls.product_category = cls.env.ref('product.product_category_5')
        cls.product_delivery = cls.env.ref('product.product_delivery_01')
        cls.product_category_account_income =  cls.product_category.property_account_income_categ_id
        cls.product_category_account_expense =  cls.product_category.property_account_expense_categ_id
        cls.account_refund_income_category = cls.env['account.account'].create({
            'name': 'Redund Income Category',
            'code': 52111,
            'user_type_id': cls.env.ref('account.data_account_type_revenue').id
        })
        cls.account_refund_expense_category = cls.env['account.account'].create({
            'name': 'Redund Expense Category',
            'code': 62111,
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id
        })
        cls.account_refund_income_product = cls.env['account.account'].create({
            'name': 'Redund Income Product',
            'code': 52112,
            'user_type_id': cls.env.ref('account.data_account_type_revenue').id
        })
        cls.account_refund_expense_product = cls.env['account.account'].create({
            'name': 'Redund Expense Product',
            'code': 62112,
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id
        })
        cls.product_category.write({
            'property_account_income_refund_categ_id': cls.account_refund_income_category,
            'property_account_expense_refund_categ_id': cls.account_refund_expense_category
        })
        cls.product_delivery.write({
            'property_account_income_refund_id': cls.account_refund_income_product,
            'property_account_expense_refund_id': cls.account_refund_expense_product
        })
        
    @classmethod
    def init_invoice(cls, move_type):
        move_form = Form(cls.env['account.move'].with_context(default_type=move_type))
        move_form.partner_id = cls.partner
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = cls.product_delivery
        return move_form.save()
    
    def test_not_config_refund_account(self):
        self.product_category.write({
            'property_account_income_refund_categ_id': False,
            'property_account_expense_refund_categ_id': False
        })
        self.product_delivery.write({
            'property_account_income_refund_id': False,
            'property_account_expense_refund_id': False
        })
        invoice = self.init_invoice('out_refund')
        self.assertEqual(invoice.invoice_line_ids[0].account_id, self.product_category_account_income)
    
    def test_onchange_refund_account_category(self):
        self.product_delivery.write({
            'property_account_income_refund_id': False,
            'property_account_expense_refund_id': False
        })
        invoice = self.init_invoice('out_refund')
        self.assertEqual(invoice.invoice_line_ids[0].account_id, self.account_refund_income_category)
        self.assertIn(invoice.invoice_line_ids.mapped('account_id'), self.account_refund_income_category)
        invoice = self.init_invoice('in_refund')
        self.assertEqual(invoice.invoice_line_ids[0].account_id, self.account_refund_expense_category)
        self.assertIn(invoice.invoice_line_ids.mapped('account_id'), self.account_refund_expense_category)
        
    def test_onchange_refund_account_product(self):
        invoice = self.init_invoice('out_refund')
        self.assertEqual(invoice.invoice_line_ids[0].account_id, self.account_refund_income_product)
        self.assertIn(invoice.invoice_line_ids.mapped('account_id'), self.account_refund_income_product)
        invoice = self.init_invoice('in_refund')
        self.assertEqual(invoice.invoice_line_ids[0].account_id, self.account_refund_expense_product)
        self.assertIn(invoice.invoice_line_ids.mapped('account_id'), self.account_refund_expense_product)
    
    def test_add_credit_note(self):
        invoice = self.init_invoice('out_invoice')
        invoice.action_post()
        wizard = self.env['account.move.reversal'].create({
            'move_id': invoice.id,
            'refund_method': 'cancel'
        })
        refund = invoice._reverse_moves([wizard._prepare_default_reversal(invoice)], cancel=True)
        self.assertEqual(invoice.invoice_payment_state, 'paid')
        self.assertEqual(refund.invoice_line_ids[0].account_id, self.account_refund_income_product)
        self.assertIn(refund.invoice_line_ids.mapped('account_id'), self.account_refund_income_product)
    
    def test_add_credit_note_2(self):
        invoice = self.init_invoice('in_invoice')
        invoice.action_post()
        wizard = self.env['account.move.reversal'].create({
            'move_id': invoice.id,
            'refund_method': 'cancel'
        })
        refund = invoice._reverse_moves([wizard._prepare_default_reversal(invoice)], cancel=True)
        self.assertEqual(invoice.invoice_payment_state, 'paid')
        self.assertEqual(refund.invoice_line_ids[0].account_id, self.account_refund_expense_product)
        self.assertIn(refund.invoice_line_ids.mapped('account_id'), self.account_refund_expense_product)
