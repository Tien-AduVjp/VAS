from datetime import datetime

from odoo.tests import Form, tagged

from odoo.addons.to_bank_currency_rate.tests.common import Common

@tagged('post_install', '-at_install')
class TestCurrencyRatePurchaseStock(Common):

    @classmethod
    def setUpClass(cls):
        super(TestCurrencyRatePurchaseStock, cls).setUpClass()

        cls.env.user.groups_id = [(4, cls.env.ref('stock.group_adv_location').id)]

        cls.product = cls.env.ref('product.consu_delivery_01')
        route_buy = cls.env['stock.location.route'].search([('name', '=', 'Buy')])
        cls.product.route_ids = [(4, route_buy.id)]

        cls.partner = cls.env['res.partner'].create({
            'name': 'vendor'
            })

        # Clean data purchase order, order point, supply info
        all_po = cls.env['purchase.order'].search([])
        all_po.button_cancel()
        all_po.unlink()
        cls.env['stock.warehouse.orderpoint'].search([]).unlink()
        cls.product.seller_ids.unlink()

        with Form(cls.product) as product:
            with product.seller_ids.new() as seller:
                seller.name = cls.partner
                seller.min_qty = 5
                seller.price = 1
                seller.currency_id = cls.vnd

        with Form(cls.env['stock.warehouse.orderpoint']) as order_point:
            order_point.product_id = cls.product
            order_point.product_min_qty = 5
            order_point.product_max_qty = 10

    @classmethod
    def create_po(cls, product=False, qty=5, currency=False, date=datetime.now()):
        po_form = Form(cls.env['purchase.order'])
        po_form.partner_id = cls.partner
        po_form.currency_id = currency or cls.env.company.currency_id
        po_form.date_order = date
        with po_form.order_line.new() as po_line:
            po_line.product_id = product or cls.product
            po_line.product_qty = qty
        po = po_form.save()
        return po, po.order_line[-1:]

    @classmethod
    def run_schedule_resupply(cls):
        cls.env['procurement.group'].run_scheduler(company_id=cls.env.company.id)

    def test_rate_autofill_po_create_manual_have_bank_default(self):
        _, po_line = self.create_po(date='2021-05-05')
        self.assertEqual(po_line.price_unit, 10000)

        _, po_line = self.create_po(date='2021-08-08')
        self.assertEqual(po_line.price_unit, 20000)

    def test_rate_autofill_po_create_manual_have_bank_default_but_no_rate(self):
        self.env.company.main_currency_bank_id = self.bank_no_rate

        _, po_line = self.create_po(date='2021-05-05')
        self.assertEqual(po_line.price_unit, 15000)

        _, po_line = self.create_po(date='2021-08-08')
        self.assertEqual(po_line.price_unit, 25000)

    def test_rate_autofill_po_create_manual_not_have_bank_default(self):
        self.env.company.main_currency_bank_id = False

        _, po_line = self.create_po(date='2021-05-05')
        self.assertEqual(po_line.price_unit, 18000)

        _, po_line = self.create_po(date='2021-08-08')
        self.assertEqual(po_line.price_unit, 28000)

    def test_supply_po_rate_have_bank_default(self):
        self.run_schedule_resupply()
        po_supply = self.env['purchase.order'].search([])
        self.assertEqual(po_supply.order_line.price_unit, 20000)

    def test_supply_po_rate_have_bank_default_no_rate(self):
        self.env.company.main_currency_bank_id = self.bank_no_rate

        self.run_schedule_resupply()
        po_supply = self.env['purchase.order'].search([])
        self.assertEqual(po_supply.order_line.price_unit, 25000)

    def test_supply_po_rate_no_have_bank_default(self):
        self.env.company.main_currency_bank_id = False

        self.run_schedule_resupply()
        po_supply = self.env['purchase.order'].search([])
        self.assertEqual(po_supply.order_line.price_unit, 28000)

    def test_rate_multi_company(self):
        origin_company = self.env.company
        company2_form = Form(self.env['res.company'])
        company2_form.name = 'company2'
        self.env.company = company2_form.save()
        self.create_rate(self.vnd, 990000, self.bank_default, 'sell_rate', '2021-05-05', '2021-05-05 05:00:00')

        _, po_line = self.create_po(date='2021-05-05')
        self.assertEqual(po_line.price_unit, 990000)
        self.env.company = origin_company
