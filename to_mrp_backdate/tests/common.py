from odoo.tests import tagged

from odoo.tests.common import SingleTransactionCase, Form


@tagged('post_install', '-at_install')
class TestCommon(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        
        user_group_stock_user = cls.env.ref('stock.group_stock_user')
        user_group_mrp_user = cls.env.ref('mrp.group_mrp_user')
        user_group_mrp_manager = cls.env.ref('mrp.group_mrp_manager')
        user_group_mrp_byproducts = cls.env.ref('mrp.group_mrp_byproducts')

        # User Data: mrp user and mrp manager
        Users = cls.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True})
        cls.user_mrp_user = Users.create({
            'name': 'Mark User',
            'login': 'user',
            'email': 'm.u0@example.viindoo.com',
            'groups_id': [(6, 0, [
                user_group_mrp_user.id,
                user_group_stock_user.id,
                user_group_mrp_byproducts.id
            ])]})
        
        cls.user_mrp_manager = Users.create({
            'name': 'Mark Lead',
            'login': 'user manager',
            'email': 'm.u@example.viindoo.com',
            'groups_id': [(6, 0, [
                user_group_mrp_manager.id,
                user_group_stock_user.id,
                user_group_mrp_byproducts.id
            ])]})
        
        # Prepare data to create MO
        Product = cls.env['product.product']
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
        
        routing = cls.env['mrp.routing'].create({
            'name': 'Simple Line',
        })
        
        cls.workcenter = cls.env['mrp.workcenter'].create({
            'name': 'Nuclear Workcenter',
            'capacity': 2,
            'time_start': 10,
            'time_stop': 5,
            'time_efficiency': 80,
        })
        
        cls.env['mrp.routing.workcenter'].create({
            'name': 'Gift Wrap Maching',
            'workcenter_id': cls.workcenter.id,
            'routing_id': routing.id,
            'time_cycle': 15,
            'sequence': 1,
        })
        
        cls.bom_route = cls.env['mrp.bom'].create({
            'product_id': cls.product_final.id,
            'product_tmpl_id': cls.product_1.product_tmpl_id.id,
            'product_uom_id': cls.product_2.uom_id.id,
            'product_qty': 1.0,
            'routing_id': routing.id,
            'type': 'normal',
            'sequence': 2,
            'bom_line_ids': [
                (0, 0, {'product_id': cls.product_1.id, 'product_qty': 2}),
                (0, 0, {'product_id': cls.product_2.id, 'product_qty': 3})
            ]})
        
        cls.bom_noroute = cls.env['mrp.bom'].create({
            'product_id': cls.product_final.id,
            'product_tmpl_id': cls.product_1.product_tmpl_id.id,
            'product_uom_id': cls.product_2.uom_id.id,
            'product_qty': 1.0,
            'type': 'normal',
            'sequence': 2,
            'bom_line_ids': [
                (0, 0, {'product_id': cls.product_1.id, 'product_qty': 2}),
                (0, 0, {'product_id': cls.product_2.id, 'product_qty': 3})
            ]})
                
        # Data for test popup transaction
        cls.mo1, cls.workorder1 = cls.generate_mo_with_workorder()
        cls.workorder1 = cls.workorder1.with_context(open_mrp_workorder_backdate_wizard=True)

        # Data for test change backdate transaction
        cls.mo2, cls.workorder2 = cls.generate_mo_with_workorder()

        cls.loss_block_type = cls.env.ref('mrp.block_reason1')
        cls.loss_reduce_type = cls.env.ref('mrp.block_reason4')
        cls.loss_fullytime_type = cls.env.ref('mrp.block_reason7')

    @classmethod
    def change_quant_product(cls, product, quant=999):
        inventory_wizard = cls.env['stock.change.product.qty'].create({
            'product_id': product.id,
            'product_tmpl_id': product.product_tmpl_id.id,
            'new_quantity': quant,
        })
        inventory_wizard.change_product_qty()
        
    @classmethod
    def generate_mo_opened_produce(cls):
        mo_form = Form(cls.env['mrp.production'])
        mo_form.product_id = cls.product_final
        mo_form.bom_id = cls.bom_noroute
        mo_form.product_qty = 1.0
        mo = mo_form.save()
        mo.action_confirm()
        mo.action_assign()
        
        # produce product
        produce_form = Form(cls.env['mrp.product.produce'].with_context({
            'active_id': mo.id,
            'active_ids': [mo.id],
        }))
        
        produce_form.qty_producing = 1.0
        product_produce = produce_form.save()
        product_produce.do_produce()
        return mo
    
    @classmethod
    def generate_mo_with_workorder(cls):
        mo_form = Form(cls.env['mrp.production'])
        mo_form.product_id = cls.product_final
        mo_form.bom_id = cls.bom_route
        mo_form.product_qty = 1.0
        
        mo = mo_form.save()
        mo.action_confirm()
        mo.action_assign()
        mo.button_plan()
        return mo, mo.workorder_ids
