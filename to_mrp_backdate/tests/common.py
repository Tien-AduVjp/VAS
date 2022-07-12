from odoo.tests import tagged
from odoo import fields
from odoo.tests.common import SavepointCase, Form


@tagged('post_install', '-at_install')
class TestCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        user_group_stock_user = cls.env.ref('stock.group_stock_user')
        user_group_mrp_user = cls.env.ref('mrp.group_mrp_user')
        user_group_mrp_manager = cls.env.ref('mrp.group_mrp_manager')
        user_group_mrp_byproducts = cls.env.ref('mrp.group_mrp_byproducts')
        user_group_mrp_backdate = cls.env.ref('to_mrp_backdate.group_mrp_backdate')

        # User Data: mrp user, mrp backdate user, mrp manager
        Users = cls.env['res.users'].with_context({'no_reset_password': True,'tracking_disable': True, 'mail_create_nosubscribe': True})
        cls.user_mrp_user = Users.create({
            'name': 'Mark User',
            'login': 'user',
            'groups_id': [(6, 0, [
                user_group_mrp_user.id,
                user_group_stock_user.id,
                user_group_mrp_byproducts.id
            ])]})

        cls.user_mrp_backdate = Users.create({
            'name': 'Mark Lead',
            'login': 'user mrp backdate',
            'groups_id': [(6, 0, [
                user_group_mrp_backdate.id,
                user_group_stock_user.id,
                user_group_mrp_byproducts.id
            ])]})

        cls.user_mrp_manager = Users.create({
            'name': 'Mark Lead',
            'login': 'user manager',
            'groups_id': [(6, 0, [
                user_group_mrp_manager.id,
                user_group_stock_user.id,
                user_group_mrp_byproducts.id
            ])]})

        # Prepare data to create MO
        Product = cls.env['product.product'].with_context(tracking_disable=True)
        cls.product_final = Product.create({
            'name': 'Chair',
            'type': 'product',
        })

        cls.product_1 = Product.create({
            'name': 'Wood',
            'type': 'product',
        })
        cls.product_2 = Product.create({
            'name': 'Stone',
            'type': 'product',
        })

        cls.change_quant_product(cls.product_1)
        cls.change_quant_product(cls.product_2)

        cls.workcenter = cls.env['mrp.workcenter'].with_context(tracking_disable=True).create({
            'name': 'Nuclear Workcenter',
            'capacity': 1,
            'time_start': 10,
            'time_stop': 5,
            'time_efficiency': 100,
        })

        cls.routing_workcenter = cls.env['mrp.routing.workcenter'].with_context(tracking_disable=True).create({
            'name': 'Gift Wrap Maching',
            'workcenter_id': cls.workcenter.id,
            'time_mode': 'manual',
            # 'routing_id': routing.id,
            'time_cycle_manual': 45,
            'sequence': 1,
        })

        cls.bom_route = cls.env['mrp.bom'].with_context(tracking_disable=True).create({
            'product_id': cls.product_final.id,
            'product_tmpl_id': cls.product_1.product_tmpl_id.id,
            'product_uom_id': cls.product_1.uom_id.id,
            'product_qty': 1.0,
            'type': 'normal',
            'sequence': 2,
            'bom_line_ids': [
                (0, 0, {'product_id': cls.product_1.id, 'product_qty': 2}),
                (0, 0, {'product_id': cls.product_2.id, 'product_qty': 3})],
            'operation_ids': cls.routing_workcenter.ids
        })

        cls.bom_noroute = cls.env['mrp.bom'].with_context(tracking_disable=True).create({
            'product_id': cls.product_final.id,
            'product_tmpl_id': cls.product_1.product_tmpl_id.id,
            'product_uom_id': cls.product_1.uom_id.id,
            'product_qty': 1.0,
            'type': 'normal',
            'sequence': 2,
            'bom_line_ids': [
                (0, 0, {'product_id': cls.product_1.id, 'product_qty': 2}),
                (0, 0, {'product_id': cls.product_2.id, 'product_qty': 3})],
            })

        cls.loss_block_type = cls.env.ref('mrp.block_reason1')

    @classmethod
    def change_quant_product(cls, product, quant=999):
        inventory_wizard = cls.env['stock.change.product.qty'].create({
            'product_id': product.id,
            'product_tmpl_id': product.product_tmpl_id.id,
            'new_quantity': quant,
        })
        inventory_wizard.change_product_qty()

    @classmethod
    def generate_mo(cls, product, bom):
        mo_form = Form(cls.env['mrp.production'])
        mo_form.product_id = product #cls.product_final
        mo_form.bom_id = bom #cls.bom_route
        mo_form.product_qty = 1.0
        mo_form.date_planned_start = fields.Datetime.to_datetime('2021-01-01')

        mo = mo_form.save()
        mo.action_confirm()
        mo.action_assign()
        return mo
