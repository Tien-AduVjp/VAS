from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase, Form, tagged


@tagged('post_install', '-at_install')
class TestToVendorPriceLock(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestToVendorPriceLock, cls).setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.product1 = cls.env['product.template'].create({
            'name': 'Produck 1'
        })
        cls.product2 = cls.env['product.template'].create({
            'name': 'Product 2'
        })
        cls.vendor1 = cls.env['res.partner'].create({
            'name': 'Vendor 1'
        })
        cls.vendor2 = cls.env['res.partner'].create({
            'name': 'Vendor 2'
        })
        cls.vendor_pricelists1 = cls.env['product.supplierinfo'].create({
            'name': cls.vendor1.id,
            'product_tmpl_id': cls.product1.id,
            'price': 123456
        })
        cls.user1 = cls.env['res.users'].create({
            'name': 'Test',
            'login': 'test login',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])]
        })
        cls.purchase_user = cls.env['res.users'].create({
            'name': 'Purchase User',
            'login': 'purchase user test',
            'groups_id': [(6, 0, cls.env.ref('purchase.group_purchase_user').ids)]
        })
        cls.purchase_manager = cls.env['res.users'].create({
            'name': 'Purchase Manager',
            'login': 'Purchase Manager',
            'groups_id': [(6, 0, [cls.env.ref('purchase.group_purchase_manager').id])]
        })

    def test_lock_vendor_pricelists(self):
        # case 1: test lock Vendor Pricelists
        self.vendor_pricelists1.with_user(self.purchase_manager).action_lock()
        self.assertEqual(self.vendor_pricelists1.state, 'locked')

        purchase_form1 = Form(self.env['purchase.order'].with_user(self.purchase_user))
        purchase_form1.partner_id = self.vendor1

        with purchase_form1.order_line.new() as line1:
            line1.product_id = self.product1.product_variant_id
            # purchase user cannot edit unit_price when price list is locked
            with self.assertRaises(UserError):
                line1.price_unit = 1
        purchase_form1.save()

        purchase_form2 = Form(self.env['purchase.order'].with_user(self.purchase_manager))
        purchase_form2.partner_id = self.vendor1

        with purchase_form2.order_line.new() as line2:
            line2.product_id = self.product1.product_variant_id
            # purchase admin can edit unit_price when price list is locked
            line2.price_unit = 1
        purchase_form2.save()

        # case 2: unlock and purchase user can edit unit_price
        self.vendor_pricelists1.with_user(self.purchase_manager).action_unlock()
        purchase_form1 = Form(self.env['purchase.order'].with_user(self.purchase_user))
        purchase_form1.partner_id = self.vendor1

        with purchase_form1.order_line.new() as line1:
            line1.product_id = self.product1.product_variant_id
            line1.price_unit = 1
        purchase_form1.save()

    def test_multi_currency(self):
        # case 5:
        self.vendor_pricelists1.with_user(self.purchase_manager).action_lock()
        self.vendor_pricelists1.currency_id = self.env.ref('base.USD')
        self.vendor_pricelists1.price = 1000

        purchase_form = Form(self.env['purchase.order'].with_user(self.purchase_user))
        purchase_form.partner_id = self.vendor1
        purchase_form.currency_id = self.env.ref('base.VND')

        with purchase_form.order_line.new() as line:
            line.product_id = self.product1.product_variant_id

        # Expect: automatically convert currency, and user purchase edits the price unit of the purchase order line
        # when the supplier's price list is locked, there will be an error.
        self.assertNotEqual(line.price_unit, self.vendor_pricelists1.price)
        with self.assertRaises(UserError):
            line.price_unit = 1234

    def test_create(self):
        # case 3: test create
        user1 = self.env['res.users'].create({
            'name': 'user1 test',
            'login': 'user1 test',
            'groups_id': [(6, 0, [self.env.ref('base.group_system').id])]
        })

        vendor_pricelists1 = self.env['product.supplierinfo'].with_user(user1).create({
            'name': self.vendor2.id,
            'product_tmpl_id': self.product2.id,
        })
        vendor_pricelists1.action_lock()
        with self.assertRaises(UserError):
            self.env['product.supplierinfo'].with_user(user1).create({
                'name': self.vendor2.id,
                'product_tmpl_id': self.product2.id
            })

    def test_unlink(self):
        # case 4: test unlink locked Vendor Pricelists
        self.vendor_pricelists1.action_lock()
        with self.assertRaises(UserError):
            self.vendor_pricelists1.unlink()

    def test_write(self):
        self.vendor_pricelists1.action_lock()
        with self.assertRaises(UserError):
            self.vendor_pricelists1.with_user(self.purchase_user).price = 100
        self.vendor_pricelists1.with_user(self.purchase_manager).price = 200
        self.assertEqual(self.vendor_pricelists1.price, 200)
