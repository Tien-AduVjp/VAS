from odoo.tests.common import SavepointCase, tagged, Form


@tagged('post_install', '-at_install')
class TestToProductCodeSequence(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestToProductCodeSequence, cls).setUpClass()
        cls.env.company.auto_product_default_code_generation = True
        cls.product_cate1 = cls.env['product.category'].create({
            'name': 'Category Test 1',
            'product_code_prefix': 'TEST-'
        })
        cls.product1 = cls.env.ref('product.product_delivery_01')

    def test_onchange_name_categ_id(self):
        # case 1:
        with Form(self.env['product.template']) as f:
            f.name = 'Pro duck'
            self.assertIn('PD', f.default_code)

    def test_product_code_prefix_category(self):
        # case 2:
        with Form(self.env['product.template']) as f:
            f.categ_id = self.product_cate1
            f.name = 'Pro duck'
            self.assertIn('TEST-', f.default_code)

    def test_get_code_from_name(self):
        self.product1.name = 'Produck XDA'
        self.assertEqual(self.product1._get_code_from_name(), 'PX')

        self.product1.name = 'duck'
        self.assertEqual(self.product1._get_code_from_name(), 'D')

    def test_change_categ_name(self):
        # case 4:
        with Form(self.env['product.template']) as f:
            f.name = 'Produck'
            f.categ_id = self.product_cate1
        product = f.save()
        self.assertIn('TEST-', product.default_code)
        product.categ_id.product_code_prefix = 'CATEG-'
        self.assertIn('TEST-', product.default_code)

    def test_onchange_not_allow_generate_default_code(self):
        """
        Case 5: Không thiết lập cho phép tạo mã sản trong thiết lập công ty
        Input: Tạo sản phẩm, Không thiết lập cho phép tạo mã trong công ty
        Output: Không tự động tạo mã sản phẩm mặc định
        """
        self.env.company.auto_product_default_code_generation = False
        with Form(self.env['product.template']) as f:
            f.name = 'Pro duck'
            self.assertFalse(f.default_code)
