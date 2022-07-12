from datetime import datetime, timedelta

from odoo.tests import SavepointCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestBackDate(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestBackDate, cls).setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.user_sale = cls.env['res.users'].create({
            'name': 'Mark User',
            'login': 'user',
            'email': 'm.u0@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('sales_team.group_sale_salesman').id])]
        })

        cls.user_sale_lead = cls.env['res.users'].create({
            'name': 'Mark Lead',
            'login': 'userlead',
            'email': 'm.u@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('sales_team.group_sale_salesman_all_leads').id])]
        })

        cls.user_sale_manager = cls.env['res.users'].create({
            'name': 'Mark Manager',
            'login': 'usermanager',
            'email': 'm.u@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('sales_team.group_sale_manager').id])]
        })

        partner = cls.env['res.partner'].create({'name': 'A'})

        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': partner.id,
            'user_id': cls.user_sale.id
        })

    def test_display_popup_backdate(self):
        so_backdate = self.sale_order.with_context({'launch_confirmation_wizard':True})

        # Case user salesman
        confirm_sale = so_backdate.with_user(self.user_sale).action_confirm()
        self.assertEqual(confirm_sale, True, 'Popup displayed with salesman!')

        # Case user sale all lead
        confirm_sale = so_backdate.with_user(self.user_sale_lead).action_confirm()
        self.assertEqual(confirm_sale.get('type'), 'ir.actions.act_window', 'Popup does not display with salesman all leads!')

        # Case user sale manager
        confirm_sale = so_backdate.with_user(self.user_sale_manager).action_confirm()
        self.assertEqual(confirm_sale.get('type'), 'ir.actions.act_window', 'Popup does not display with sale manager!')

    def test_input_backdate_future(self):
        with self.assertRaises(UserError):
            self.env['wizard.confirm.sale'].create({
                'sale_order_id':self.sale_order.id,
                'date': datetime.now() + timedelta(days=1)
            })

    def test_change_time_backdate(self):
        backdate = datetime(2021, 5, 17)
        WizardConfirmSale = self.env['wizard.confirm.sale'].create({
            'sale_order_id': self.sale_order.id,
            'date': backdate
        })
        WizardConfirmSale.process()

        self.assertEqual(self.sale_order.date_order, backdate, 'Backdate is wrong!')
