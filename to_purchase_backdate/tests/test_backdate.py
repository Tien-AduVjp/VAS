from datetime import datetime, timedelta

from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestBackDate(TransactionCase):

    def setUp(self):
        super(TestBackDate, self).setUp()

        self.backdate = datetime(2021, 5, 17)

        # Create data PO, PO line
        partner = self.env['res.partner'].create({'name': 'vendor'})
        product = self.env['product.product'].create({'name': 'Table'})

        self.purchase_order = self.env['purchase.order'].create({
            'partner_id':partner.id
        })

        self.purchase_order_line = self.env['purchase.order.line'].create({
            'name': 'purchase',
            'product_id': product.id,
            'product_qty':1,
            'order_id': self.purchase_order.id,
            'price_unit': 2000,
            'date_planned': datetime.now(),
            'product_uom': product.uom_id.id
        })

        # Create data User Purchase
        Users = self.env['res.users'].with_context({'no_reset_password': True})

        self.purchase_user = Users.create({
            'name': 'Mark User',
            'login': 'user1',
            'email': 'm.u1@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('purchase.group_purchase_user').id])]
        })

        self.purchase_admin = Users.create({
            'name': 'Mark Admin',
            'login': 'user2',
            'email': 'm.u2@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('purchase.group_purchase_manager').id])]
        })

        self.po_backdate = self.purchase_order.with_context({'launch_confirmation_wizard':True})

    def test_display_popup_backdate_user(self):
        # Test display popup when click button confirm with purchase user
        confirm_po = self.po_backdate.with_user(self.purchase_user).button_confirm()
        self.assertEqual(confirm_po, True, 'Popup displayed with purchase user!')

    def test_display_popup_backdate_admin(self):
        # Test display popup when click button confirm with purchase admin
        confirm_po = self.po_backdate.with_user(self.purchase_admin).button_confirm()
        self.assertEqual(confirm_po.get('type'), 'ir.actions.act_window', 'Popup does not display with purchase admin when click button confirm!')

    def test_display_popup_backdate_approve(self):
        # Enable purchase 2 step
        self.env.company.write({
            'po_double_validation': 'two_step',
            'po_double_validation_amount': 1000,
        })
        # Step 1: purchase user confirm
        self.po_backdate.with_user(self.purchase_user).button_confirm()

        # Step 2: Test display Popup when click button approval with purchase admin
        approval_po = self.po_backdate.with_user(self.purchase_admin).button_approve()
        self.assertEqual(approval_po.get('type'), 'ir.actions.act_window', 'Popup does not display with purchase admin when click button approve!')

    def test_input_backdate_future(self):
        with self.assertRaises(UserError):
            self.env['wizard.confirm.purchase'].create({
                'purchase_order_id':self.purchase_order.id,
                'date': datetime.now() + timedelta(days=1)
            })

    def test_time_backdate_confirm(self):
        WizardConfirmPurchase = self.env['wizard.confirm.purchase'].create({
            'purchase_order_id':self.purchase_order.id,
            'date': self.backdate
        })
        WizardConfirmPurchase.process()

        self.assertEqual(self.purchase_order.date_approve, self.backdate, 'Backdate PO when confirm is wrong!')
        self.assertEqual(self.purchase_order_line[0].date_order, self.backdate, 'Backdate PO line when confirm is wrong!')

    def test_time_backdate_approval(self):
        # Enable purchase 2 step
        self.env.company.write({
            'po_double_validation': 'two_step',
            'po_double_validation_amount': 1000,
        })

        # step 1: purchase user confirm
        self.purchase_order.with_user(self.purchase_user).button_confirm()

        WizardConfirmPurchase = self.env['wizard.confirm.purchase'].create({
            'purchase_order_id':self.purchase_order.id,
            'date': self.backdate
        })

        # step 2: validate approve backdate wizard
        WizardConfirmPurchase.process()

        self.assertEqual(self.purchase_order.date_approve, self.backdate, 'Backdate PO when approve is wrong!')
        self.assertEqual(self.purchase_order_line[0].date_order, self.backdate, 'Backdate PO line when approve is wrong!')
