from odoo.tests import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestSaleFee(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleFee, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.user_demo.groups_id = [(4, cls.env.ref('sales_team.group_sale_manager').id)]
        cls.attr = cls.env.ref('product.product_attribute_3')
        cls.service_01 = cls.env['product.product'].create({
            'name': 'Service 01',
            'lst_price': 300,
            'type': 'service',
            'categ_id': cls.env.ref('product.product_category_all').id,
            'taxes_id': [(6, 0, [])]
        })
        cls.service_02 = cls.env['product.product'].create({
            'name': 'Service 02',
            'lst_price': 400,
            'type': 'service',
            'categ_id': cls.env.ref('product.product_category_all').id,
            'taxes_id': [(6, 0, [])]
        })
        cls.service_03 = cls.env['product.template'].create({
            'name': 'Service',
            'lst_price': 500,
            'type': 'service',
            'categ_id': cls.env.ref('product.product_category_all').id,
            'taxes_id': [(6, 0, [])],
            'attribute_line_ids': [
                (0, 0, {
                    'attribute_id': cls.attr.id,
                    'value_ids': [(6, 0, [cls.attr.value_ids[0].id, cls.attr.value_ids[1].id])]
                }),
            ]
        })
        cls.service_03_a = cls.service_03.product_variant_ids[0]
        cls.service_03_b = cls.service_03.product_variant_ids[1]
        cls.virtual_service = cls.env.ref('product.product_product_2')
        cls.product_1 = cls.env['product.product'].create({
            'name': 'System 67',
            'lst_price': 1000,
            'type': 'consu',
            'categ_id': cls.env.ref('product.product_category_all').id,
            'taxes_id': [(6, 0, [])]
        })
        cls.fee_apply_to_service_01 = cls.env['fee.definition'].create({
            'product_tmpl_id': cls.service_01.product_tmpl_id.id,
            'product_id': cls.service_02.id,
            'quantity': 1,
        })
        cls.fee_apply_to_service_01__02 = cls.env['fee.definition'].create({
            'product_tmpl_id': cls.service_01.product_tmpl_id.id,
            'product_id': cls.virtual_service.id,
            'quantity': 1,
        })
        cls.fee_apply_to_service_02 = cls.env['fee.definition'].create({
            'product_tmpl_id': cls.service_02.product_tmpl_id.id,
            'product_id': cls.service_03_a.id,
            'quantity': 1,
        })
        cls.fee_apply_to_service_03 = cls.env['fee.definition'].create({
            'product_tmpl_id': cls.service_03_b.product_tmpl_id.id,
            'product_id': cls.virtual_service.id,
            'quantity': 1,
        })
        cls.fee_apply_to_product_1 = cls.env['fee.definition'].create({
            'product_tmpl_id': cls.product_1.product_tmpl_id.id,
            'product_id': cls.service_01.id,
            'quantity': 1,
        })

    def test_create_nested_fee(self):
        self.assertEqual(self.product_1.nested_fee_definition_ids,
                         self.fee_apply_to_service_01 +
                         self.fee_apply_to_service_01__02 +
                         self.fee_apply_to_service_02 +
                         self.fee_apply_to_service_03 +
                         self.fee_apply_to_product_1)

    def test_compute_fee_lst_price(self):
        self.assertEqual(self.fee_apply_to_service_01.lst_price, self.service_02.lst_price)
        self.assertEqual(self.fee_apply_to_product_1.lst_price, self.service_01.lst_price)

    def create_sale_order(self):
        return self.env['sale.order'].create({
            'partner_id': self.user_demo.partner_id.id,
            'partner_invoice_id': self.user_demo.partner_id.id,
            'partner_shipping_id': self.user_demo.partner_id.id,
            'pricelist_id': self.user_demo.partner_id.property_product_pricelist.id,
            'order_line': [(0, 0, {
                'product_id': self.product_1.id,
                'product_uom_qty': 1,
                'product_uom': self.env.ref('uom.product_uom_unit').id,
                'price_unit': self.product_1.lst_price,
                'tax_id': False
            })],
        })

    def check_order_values(self, order):
        # check order line after compute supplementary fees
        self.assertRecordValues(order.order_line,
                                [{'product_id': self.product_1.id, }, {'product_id': self.service_01.id},
                                 {'product_id': self.service_02.id}, {'product_id': self.virtual_service.id},
                                 {'product_id': self.service_03_a.id},{'product_id': self.virtual_service.id}])
        # check order line fee after compute supplementary fees
        self.assertRecordValues(order.order_line_fee_ids, [{
            'fee_line_id': order.order_line.filtered(lambda l: l.fee_for_line_ids.fee_definition_id == self.fee_apply_to_product_1).id,
            'line_id': order.order_line.filtered(lambda l: l.product_id.product_tmpl_id == self.fee_apply_to_product_1.product_tmpl_id).id,
            'quantity': 1,
            'fee_definition_id': self.fee_apply_to_product_1.id,
            'lst_price': self.fee_apply_to_product_1.sale_price
        }, {
            'fee_line_id': order.order_line.filtered(lambda l: l.fee_for_line_ids.fee_definition_id == self.fee_apply_to_service_01).id,
            'line_id': order.order_line.filtered(lambda l: l.product_id.product_tmpl_id == self.fee_apply_to_service_01.product_tmpl_id).id,
            'quantity': 1,
            'fee_definition_id': self.fee_apply_to_service_01.id,
            'lst_price': self.fee_apply_to_service_01.sale_price
        }, {
            'fee_line_id': order.order_line.filtered(lambda l: l.fee_for_line_ids.fee_definition_id == self.fee_apply_to_service_01__02).id,
            'line_id': order.order_line.filtered(lambda l: l.product_id.product_tmpl_id == self.fee_apply_to_service_01__02.product_tmpl_id).id,
            'quantity': 1,
            'fee_definition_id': self.fee_apply_to_service_01__02.id,
            'lst_price': self.fee_apply_to_service_01__02.sale_price
        }, {
            'fee_line_id': order.order_line.filtered(lambda l: l.fee_for_line_ids.fee_definition_id == self.fee_apply_to_service_02).id,
            'line_id': order.order_line.filtered(lambda l: l.product_id.product_tmpl_id == self.fee_apply_to_service_02.product_tmpl_id).id,
            'quantity': 1,
            'fee_definition_id': self.fee_apply_to_service_02.id,
            'lst_price': self.fee_apply_to_service_02.sale_price
        }, {
            'fee_line_id': order.order_line.filtered(lambda l: l.fee_for_line_ids.fee_definition_id == self.fee_apply_to_service_03).id,
            'line_id': order.order_line.filtered(lambda l: l.product_id.product_tmpl_id == self.fee_apply_to_service_03.product_tmpl_id).id,
            'quantity': 1,
            'fee_definition_id': self.fee_apply_to_service_03.id,
            'lst_price': self.fee_apply_to_service_03.sale_price
        }])

    def test_compute_supplementary_fees(self):
        order = self.create_sale_order()
        order.action_compute_fees()
        self.check_order_values(order)

    def test_wizard_confirm_sale_order_01(self):
        """ confirm sale order without compute supplementary fees"""
        order = self.create_sale_order()
        order.with_context(force_no_supplementary_fees=True).action_confirm()
        self.assertEqual(len(order.order_line), 1)
        self.assertFalse(order.order_line_fee_ids)

    def test_wizard_confirm_sale_order_02(self):
        """ confirm sale order with compute supplementary fees"""
        order = self.create_sale_order()
        wizard_confirm = self.env['sale.immediate.confirm'].create({
            'order_id': order.id
        })
        wizard_confirm.action_compute_supplementary_fees_and_confirm()
        self.check_order_values(order)
