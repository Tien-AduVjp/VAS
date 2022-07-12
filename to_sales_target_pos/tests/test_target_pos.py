from datetime import datetime, timedelta

from odoo.tests import tagged
from odoo.tests.common import Form

from odoo.addons.to_sales_target_sale.tests.common import TestTargetSaleCommon
from odoo.addons.point_of_sale.tests.test_anglo_saxon import TestAngloSaxonFlow


@tagged('post_install', '-at_install')
class TestTargetPos(TestTargetSaleCommon):
    @classmethod
    def setUpClass(cls):
        super(TestTargetPos, cls).setUpClass()

        cls.company = cls.env.ref('base.main_company')
        cls.user_salesman.groups_id = [(4, cls.env.ref('point_of_sale.group_pos_user').id)]
        cls.user_leader.groups_id = [(4, cls.env.ref('point_of_sale.group_pos_user').id)]

        cls.account = cls.env['account.account'].create({
            'name': 'Receivable',
            'code': 'RCV00',
            'user_type_id': cls.env.ref('account.data_account_type_receivable').id,
            'reconcile': True,
            })
        cls.cash_journal = cls.env['account.journal'].create({'name': 'CASH journal', 'type': 'cash', 'code': 'CSH00'})
        cls.cash_payment_method = cls.env['pos.payment.method'].create({
            'name': 'Cash Test',
            'is_cash_count': True,
            'cash_journal_id': cls.cash_journal.id,
            'receivable_account_id': cls.account.id,
        })
        cls.pos_config = cls.env.ref('point_of_sale.pos_config_main').copy({
            'name': 'New POS config',
            'payment_method_ids': [(6, 0, cls.cash_payment_method.ids)]})
        cls.pos_config.crm_team_id = cls.team1
        cls.pos_config.module_account = True

        cls.partner = cls.env.ref('base.res_partner_1')

        cls.so = cls.create_so(cls.product_sale, user_create=cls.user_salesman)

        cls.sale_target = cls.form_create_team_target(cls.team1,
                                               datetime.now(),
                                               datetime.now() + timedelta(days=31),
                                               target=160000)

        cls.sale_target_saleman = cls.sale_target.personal_target_ids.filtered(lambda r: r.sale_person_id == cls.user_salesman)
        cls.sale_target_saleman.target = 100000
        cls.sale_target_leader = cls.sale_target.personal_target_ids - cls.sale_target_saleman
        cls.sale_target_leader.target = 60000

        cls.sale_target.action_confirm()
        cls.sale_target.action_approve()

    def create_paid_pos_order(self, value=3150, invoiced=False, user_created=False):
        self.pos_config.open_session_cb()
        pos_order_values = {
            'company_id': self.company.id,
            'partner_id': self.partner.id,
            'pricelist_id': self.company.partner_id.property_product_pricelist.id,
            'session_id': self.pos_config.current_session_id.id,
            'lines': [(0, 0, {
                'name': "OL/0001",
                'product_id': self.product_sale.id,
                'price_unit': value / 7,
                'discount': 0.0,
                'qty': 7.0,
                'price_subtotal': value,
                'price_subtotal_incl': value,
            })],
            'amount_total': value,
            'amount_tax': 0,
            'amount_paid': 0,
            'amount_return': 0,
        }
        pos_order = self.env['pos.order'].with_user(user_created or self.env.user).create(pos_order_values)
        context_make_payment = {"active_ids": [pos_order.id], "active_id": pos_order.id}
        pos_make_payment = self.env['pos.make.payment'].with_context(context_make_payment).create({
            'amount': value,
            'payment_method_id': self.cash_payment_method.id,
        })
        # register the payment
        context_payment = {'active_id': pos_order.id}
        pos_make_payment.with_context(context_payment).check()

        # Create the customer invoice
        if invoiced:
            pos_order.action_pos_order_invoice()

        return pos_order

    def test_linking_pos_order_to_target(self):
        # Test POS Order, POS Order Invoiced linking to sales target
        pos_non_invoiced = self.create_paid_pos_order(user_created=self.user_salesman)
        pos_invoiced = self.create_paid_pos_order(invoiced=True, user_created=self.user_salesman)
        # Create new team target invalid
        sale_target_outrange_date = self.form_create_team_target_approve(self.team1,
                               datetime.now() + timedelta(days=32),
                               datetime.now() + timedelta(days=35),
                               target=10000)

        empty_pos_order = self.env['pos.order']

        # Get personal target invalid
        sale_target_saleman_outrange_date = sale_target_outrange_date.personal_target_ids.filtered(lambda r: r.sale_person_id == self.user_salesman)

        # The sales target date without the date on the PoS Order.
        self.assertEqual(sale_target_outrange_date.non_invoiced_pos_order_ids, empty_pos_order, "Non invoiced PoS order valid is not linked to Team target!")
        self.assertEqual(sale_target_outrange_date.non_invoiced_pos_orders_count, 0, "Count Non invoiced PoS order displayed in view Team target is incorrect!")
        self.assertEqual(sale_target_saleman_outrange_date.non_invoiced_pos_order_ids, empty_pos_order, "Non invoiced PoS order valid is not linked to Personal target!")
        self.assertEqual(sale_target_saleman_outrange_date.non_invoiced_pos_orders_count, 0, "Count Non invoiced PoS order displayed in view Personal target is incorrect!")

        self.assertEqual(sale_target_outrange_date.invoiced_pos_order_ids, empty_pos_order, "Invoiced PoS order valid is not linked to Team target!")
        self.assertEqual(sale_target_outrange_date.invoiced_pos_orders_count, 0, "Count invoiced PoS order displayed in view Team target is incorrect!")
        self.assertEqual(sale_target_saleman_outrange_date.invoiced_pos_order_ids, empty_pos_order, "Invoiced PoS order valid is not linked to Personal target!")
        self.assertEqual(sale_target_saleman_outrange_date.invoiced_pos_orders_count, 0, "Count Invoiced PoS order displayed in view Personal target is incorrect!")

        # The sales target date within the date on the PoS Order.
        self.assertEqual(self.sale_target.non_invoiced_pos_order_ids, pos_non_invoiced, "SO valid is not linked to Team target!")
        self.assertEqual(self.sale_target.non_invoiced_pos_orders_count, 1, "Count SO displayed in view Team target is incorrect!")
        self.assertEqual(self.sale_target_saleman.non_invoiced_pos_order_ids, pos_non_invoiced, "SO valid is not linked to Personal target!")
        self.assertEqual(self.sale_target_saleman.non_invoiced_pos_orders_count, 1, "Count SO displayed in view Personal target is incorrect!")

        self.assertEqual(self.sale_target.invoiced_pos_order_ids, pos_invoiced, "Invoice valid is not linked to Team target!")
        self.assertEqual(self.sale_target.invoiced_pos_orders_count, 1, "Count Invoice displayed in view Team target is incorrect!")
        self.assertEqual(self.sale_target_saleman.invoiced_pos_order_ids, pos_invoiced, "Invoice valid is not linked to Personal target!")
        self.assertEqual(self.sale_target_saleman.invoiced_pos_orders_count, 1, "Count Invoice displayed in view Personal target is incorrect!")

    def test_compute_sales_kpi_on_target(self):
        team_target = self.sale_target.target
        saleman_target = self.sale_target_saleman.target
        leader_target = self.sale_target_leader.target

        # Stage1
        salesman_value = 2022
        order_salesman = self.create_paid_pos_order(value=salesman_value, user_created=self.user_salesman)

        leader_value_invoiced = 3333
        self.create_paid_pos_order(value=leader_value_invoiced, invoiced=True, user_created=self.user_leader)

        # Team target
        self.assertEqual(self.sale_target.non_invoiced_pos_sales_total, salesman_value)
        self.assertEqual(self.sale_target.invoiced_pos_sales_total, leader_value_invoiced)
        self.assertEqual(self.sale_target.pos_sales_total, salesman_value + leader_value_invoiced)
        self.assertEqual(self.sale_target.pos_sales_target_reached, (salesman_value + leader_value_invoiced) * 100 / team_target)
        self.assertEqual(self.sale_target.sales_total, salesman_value + leader_value_invoiced)
        self.assertEqual(self.sale_target.target_reached, (salesman_value + leader_value_invoiced) * 100 / team_target)
        # Salesman target
        self.assertEqual(self.sale_target_saleman.non_invoiced_pos_sales_total, salesman_value)
        self.assertEqual(self.sale_target_saleman.invoiced_pos_sales_total, 0)
        self.assertEqual(self.sale_target_saleman.pos_sales_total, salesman_value)
        self.assertEqual(self.sale_target_saleman.pos_sales_target_reached, salesman_value * 100 / saleman_target)
        self.assertEqual(self.sale_target_saleman.sales_total, salesman_value)
        self.assertEqual(self.sale_target_saleman.target_reached, salesman_value * 100 / saleman_target)
        # Leader target
        self.assertEqual(self.sale_target_leader.non_invoiced_pos_sales_total, 0)
        self.assertEqual(self.sale_target_leader.invoiced_pos_sales_total, leader_value_invoiced)
        self.assertEqual(self.sale_target_leader.pos_sales_total, leader_value_invoiced)
        self.assertEqual(self.sale_target_leader.pos_sales_target_reached, leader_value_invoiced * 100 / leader_target)
        self.assertEqual(self.sale_target_leader.sales_total, leader_value_invoiced)
        self.assertEqual(self.sale_target_leader.target_reached, leader_value_invoiced * 100 / leader_target)

        # Stage2
        so = self.create_so(self.product_sale, user_create=self.user_salesman)
        invoice = self.create_posted_invoice_from_so(so)
        invoice_value = invoice.amount_untaxed

        # Team target
        self.assertEqual(self.sale_target.sales_total, salesman_value + leader_value_invoiced + invoice_value)
        self.assertEqual(self.sale_target.target_reached, (salesman_value + leader_value_invoiced + invoice_value) * 100 / team_target)
        # Salesman target
        self.assertEqual(self.sale_target_saleman.sales_total, salesman_value + invoice_value)
        self.assertEqual(self.sale_target_saleman.target_reached, (salesman_value + invoice_value) * 100 / saleman_target)
        # Leader target
        self.assertEqual(self.sale_target_leader.sales_total, leader_value_invoiced)
        self.assertEqual(self.sale_target_leader.target_reached, leader_value_invoiced * 100 / leader_target)
