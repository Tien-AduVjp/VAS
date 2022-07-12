# -*- coding: utf-8 -*-

from odoo.tests import SavepointCase, Form
from odoo import fields
from odoo.addons.mrp.tests.common import TestMrpCommon


class TestUnbuildCheckSvl(SavepointCase):

    @classmethod
    def setUpClass(cls):
        '''
            We cannot re-use any test of MRP since we need to test the BoM with price percentage.
            Their tests don't have these fields
            Noreover, the Common file in mrp has lots more data created that we dont use in here
        '''
        super().setUpClass()

        cls.fifo_categ = cls.env.ref('product.product_category_6')
        cls.fifo_categ.write({
            'property_cost_method': 'fifo',
            'property_valuation': 'real_time',
        })

        cls.product_to_build = cls.env['product.product'].create({
            'name': 'Product To Build',
            'type': 'product',
            'categ_id': cls.fifo_categ.id,
        })
        # standard_price = $10
        # No tracking
        cls.product_component_1 = cls.env.ref('product.product_product_9')
        cls.product_component_1.categ_id = cls.fifo_categ.id
        # standard_price = $12.50
        # No tracking
        cls.product_component_2 = cls.env.ref('product.product_product_10')
        cls.product_component_2.categ_id = cls.fifo_categ.id

        cls.routing = cls.env.ref('mrp.mrp_routing_0')
        cls.work_center = cls.env.ref('mrp.mrp_workcenter_2')
        cls.work_center.costs_hour = 100000000

        cls.bom = cls.env['mrp.bom'].create({
            'product_id': cls.product_to_build.id,
            'product_tmpl_id': cls.product_to_build.product_tmpl_id.id,
            'product_uom_id': cls.env.ref('uom.product_uom_unit').id,
            'product_qty': 1.0,
            'routing_id': cls.routing.id,
            'type': 'normal',
            'company_id': cls.env.company.id,
            'bom_line_ids': [
                (0, 0, {'product_id': cls.product_component_1.id, 'product_qty': 1, 'price_percent': 60}),
                (0, 0, {'product_id': cls.product_component_2.id, 'product_qty': 1, 'price_percent': 40}),
            ]})

    def _create_mo(self):
        f = Form(self.env['mrp.production'])
        f.product_id = self.product_to_build
        f.product_uom_id = self.product_to_build.uom_id
        f.product_qty = 1
        f.bom_id = self.bom
        manufacturing_order = f.save()

        manufacturing_order.action_confirm()
        manufacturing_order.action_assign()
        manufacturing_order.button_plan()

        test_workorder = manufacturing_order.workorder_ids[:1]
        test_workorder.button_start()
        test_workorder.record_production()

        manufacturing_order.button_mark_done()

        return manufacturing_order

    def test_01(self):
        '''
            Input:
                Unbuild a BoM with related Manufacturing Order
                Note:
                    The cost of work center will be 0, because we only want to
                    test on unit price based the price percent on each product.
                    
                    How much the 'product_to_build' cost after has been manufactured
                    doesn't really matter.  
            Expect:
                The produced component products get the unit cost updated
                according to the price percent assigned on the BoM
                    produce_component_1 = 22.5 * 60% = 13.5
                    produce_component_2 = 22.5 * 40% =  9.0
        '''
        test_manufacturing_order = self._create_mo()

        # unbuild order with manufacturing order
        test_unbuild_order = self.env['mrp.unbuild'].create({
            'mo_id': test_manufacturing_order.id,
            'product_qty': 1,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'product_id': test_manufacturing_order.product_id.id,
            'bom_id': test_manufacturing_order.bom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
        })
        test_unbuild_order.action_validate()

        svls = test_unbuild_order.produce_line_ids.stock_valuation_layer_ids
        svl_prod_to_unbuild = svls.filtered(lambda svl: svl.product_id.id == self.product_to_build.id)
        svl_prod_comp_1 = svls.filtered(lambda svl: svl.product_id.id == self.product_component_1.id)
        svl_prod_comp_2 = svls.filtered(lambda svl: svl.product_id.id == self.product_component_2.id)
        
        # Expect unit cost = 22.5 due to cost of work center = 0 since we start and stop instantly
        # 22.5 * 60% = 13.5
        # 22.5 * 40% =  9.0
        self.assertRecordValues(svl_prod_to_unbuild, [{'unit_cost': 22.5, 'quantity': -1}])
        self.assertRecordValues(svl_prod_comp_1, [{'unit_cost': 13.5, 'quantity': 1}])
        self.assertRecordValues(svl_prod_comp_2, [{'unit_cost': 9.0, 'quantity': 1}])

    def test_02(self):
        '''
            Input:
                Purchased the Product To Build with price = 100.000
                Then unbuild this product using it's BoM
            Expect:
                The produced component products get the unit cost updated
                according to the price percent assigned on the BoM:
                    produce_component_1 = 100.000 * 60% = 60.000
                    produce_component_2 = 100.000 * 40% = 40.000
        '''
        test_po = self.env['purchase.order'].create({
            'partner_id': self.env.ref('base.partner_admin').id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product_to_build.id,
                    'date_planned': fields.Datetime.now(),
                    'name': self.product_to_build.name,
                    'product_qty': 1,
                    'product_uom': 1,
                    'price_unit': 100000,
                    'taxes_id': False
                })
            ]
        })
        test_po.button_confirm()

        test_receipt = test_po.picking_ids[0]

        for move_line in test_receipt.move_ids_without_package:
            move_line.quantity_done = move_line.product_uom_qty

        test_receipt.button_validate()

        # unbuild order without manufacturing order
        test_unbuild_order = self.env['mrp.unbuild'].create({
            'product_qty': 1,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'product_id': self.product_to_build.id,
            'bom_id': self.bom.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
        })
        test_unbuild_order.action_validate()

        svls = test_unbuild_order.produce_line_ids.stock_valuation_layer_ids
        svl_prod_to_unbuild = svls.filtered(lambda svl: svl.product_id.id == self.product_to_build.id)
        svl_prod_comp_1 = svls.filtered(lambda svl: svl.product_id.id == self.product_component_1.id)
        svl_prod_comp_2 = svls.filtered(lambda svl: svl.product_id.id == self.product_component_2.id)
        
        # Expect unit cost = 100000 due to cost of work center = 0 since we start and stop instantly
        # 100.000 * 60% = 60000
        # 100.000 * 40% = 40000
        self.assertRecordValues(svl_prod_to_unbuild, [{'unit_cost': 100000, 'quantity': -1}])
        self.assertRecordValues(svl_prod_comp_1, [{'unit_cost': 60000, 'quantity': 1}])
        self.assertRecordValues(svl_prod_comp_2, [{'unit_cost': 40000, 'quantity': 1}])
