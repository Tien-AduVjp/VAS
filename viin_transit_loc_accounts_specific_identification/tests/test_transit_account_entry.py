from odoo.tests import tagged

from odoo.addons.to_transit_loc_accounts.tests.common import TestTransitTransferCommon
from odoo.addons.viin_stock_specific_identification.tests.test_svl_common import TestSVLCommon


@tagged('-at_install', 'post_install')
class TestTransitAccountTrySpecificIdentification(TestTransitTransferCommon, TestSVLCommon):
    
    def test_transfer_product_tracking_serial(self):
        '''
            Input:
                Warehouse
                    A sub warehouse, SWH, with resupply from the WH warehouse
                Route
                    Route for resupply:
                        . WH/stock -> transit location
                        . transit location -> sub warehouse
                        . where:
                            transit location has Accounts
                        . consists of 2 rules
                Rule:
                    1)
                        . pull rule
                        . make from stock
                        . from Wh/stock location
                        . to transit location
                    2)
                        . pull rule
                        . mfs_else_mfo
                        . from transit location
                        . to sub warehouse location
                Product 1
                    Type:            storagable
                    tracking:        serial
                    cost_method:     specific identification
                    valuation:       automated
                    route_ids:       route for resupply
                Reordering Rule
                    Location:        sub-warehouse locatin
                    Min              2
                    Max              4

                Product 2
                    Type:            storagable
                    tracking:        lot
                    cost_method:     specific identification
                    valuation:       automated
                    route_ids:       route for resupply
                Reordering Rule
                    Location:        sub-warehouse locatin
                    Min              2
                    Max              5
                    
            Process:
                1) Buy product 1 with quantity = 10 and cost = 5
                2) Buy product 1 with quantity = 5 and cost = 3
                3) Buy product 2 with quantity = 5 and cost = 150
                4) Buy product 2 with quantity = 5 and cost = 250
                3) Run Scheduler
            
            Expect:
                2 new stock.moves generated:
                    1 with 
                        status 'wait for another'
                        from WH/stock
                        to transit loc
                        5 move lines (4 serial, 1 lot)
                    1 with
                        status 'need confirm'
                        from transit loc
                        to SWH/stock
                        5 move lines (4 serial, 1 lot)
                Validate moves generated:
                    5 journal entry (4 serial, 1 lot)
                    5 svl (4 serial, 1 lot)
        '''
        # ------------------------ #
        # ---     WAREHOUSE    --- #
        # ------------------------ #
        sub_warehouse = self.env['stock.warehouse'].create({
            'name': 'My Sub Warehouse (San Francisco)',
            'code': 'SWH',
            'company_id': self.env.company.id,
        })
        sub_warehouse.resupply_wh_ids = [(6, 0, [self.env.ref('stock.warehouse0').id])]

        sub_warehouse_location = sub_warehouse.lot_stock_id

        # -------------------- #
        # ---     ROUTE    --- #
        # -------------------- #
        resupply_route = sub_warehouse.resupply_route_ids.filtered(
            lambda sr: 'My Sub Warehouse (San Francisco)' in sr.name
        )

        # The resupply route has 2 rules
        #     1 from WH/stock to transit location
        #     1 from transit to SubWH/Stock location
        #
        # Update Accounts on the transit location
        route_rule_inter_to_transit = resupply_route.rule_ids.filtered(
            lambda r: r.location_src_id.id == self.wh_stock_internal_location.id
        )

        test_transit_location = route_rule_inter_to_transit.location_id
        account = self.env['account.account'].search([('company_id', '=', self.env.company.id)], limit=2)
        test_transit_location.write({
            'valuation_in_account_id': account[0].id,
            'valuation_out_account_id': account[1].id
        })

        # ---------------------- #
        # ---     PRODUCT    --- #
        # ---------------------- #
        identify_method = self.env['product.category'].create({
            'name': 'identification',
            'property_cost_method': 'specific_identification',
            'property_valuation': 'real_time'
        })

        # We're gonna use "Run Scheduler" feature from Inventory module
        # to create 2 stock moves at the same times
        #
        # We create new product for avoiding complicatation on checking assert
        product_1 = self.env['product.product'].create({
            'name': 'Product to Test 1',
            'type': 'product',
            'tracking': 'serial',
            'categ_id': identify_method.id,
            'route_ids': [(4, resupply_route.id)]
        })

        product_2 = self.env['product.product'].create({
            'name': 'Product to Test 2',
            'type': 'product',
            'tracking': 'lot',
            'categ_id': identify_method.id,
            'route_ids': [(4, resupply_route.id)]
        })

        # ------------------------------ #
        # ---     REORDERING RULE    --- #
        # ------------------------------ #

        # Note:
        #    Value of 'warehouse_id' and 'route_id'
        #
        #    We dont have to enter these values when creating new orderpoint using Form
        #    But they are required on ORM for the logic to be able to find the corresponding reordering rules
        self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': sub_warehouse.id,
            'location_id': sub_warehouse.lot_stock_id.id,
            'product_min_qty': 2,
            'product_max_qty': 4,
            'product_id': product_1.id,
        })
        self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': sub_warehouse.id,
            'location_id': sub_warehouse.lot_stock_id.id,
            'product_min_qty': 2,
            'product_max_qty': 5,
            'product_id': product_2.id,
        })
        # -------------------------------------------------- #
        # General check before moving on                     #
        # -------------------------------------------------- #

        # Resupply from WH
        self.assertEqual(sub_warehouse.resupply_wh_ids.ids, [self.env.ref('stock.warehouse0').id])
        self.assertTrue(sub_warehouse_location)

        self.assertEqual(len(resupply_route.rule_ids), 2)
        self.assertRecordValues(route_rule_inter_to_transit, [{
            'action': 'pull',
            'location_src_id': self.wh_stock_internal_location.id,
            'location_id': test_transit_location.id,
            'procure_method': 'make_to_stock',
            'warehouse_id': self.env.ref('stock.warehouse0').id
        }])
        self.assertRecordValues(resupply_route.rule_ids[1], [{
            'action': 'pull',
            'location_src_id': test_transit_location.id,
            'location_id': sub_warehouse.lot_stock_id.id,
            'procure_method': 'make_to_order',
            'warehouse_id': sub_warehouse.id
        }])
        self.assertTrue(test_transit_location.valuation_in_account_id)
        self.assertTrue(test_transit_location.valuation_out_account_id)

        # -------------------------------------------------- #
        # Buy this product with 10 units price 5 and 5 units price 3, respectively #
        # -------------------------------------------------- #
        in_move_lot_1 = self._create_in_move(product_2, 150, 5)
        in_move_lot_2 = self._create_in_move(product_2, 250, 5)
        
        in_move_serial_1 = self._create_in_move(product_1, 5, 10)    
        in_move_serial_2 = self._create_in_move(product_1, 3, 5)
        
        picking = self._create_picking(in_move_serial_1 | in_move_serial_2 | in_move_lot_1)
        self._generate_sn(picking.move_lines)
        self._generate_lot(picking.move_lines, 1)
        picking.button_validate()

        picking = self._create_picking(in_move_lot_2)
        self._generate_lot(picking.move_lines, 1)
        picking.button_validate()

        # ----------------------- #
        # execute Run Scheduler   #
        # ----------------------- #
        self.env['procurement.group'].run_scheduler(company_id=self.env.company.id)

        # Retrieve the 2 stock pickings that are just following the reordering rule
        receipt_moves = self.env['stock.picking'].search([
            ('product_id', '=', product_1.id),
            '|',
                ('location_id', '=', test_transit_location.id),
                ('location_dest_id', '=', test_transit_location.id)
        ])

        self.assertEqual(len(receipt_moves), 2)

        picking_waiting = receipt_moves.filtered(lambda m: m.state == 'waiting')
        picking_assigned = receipt_moves - picking_waiting

        # Validate first stock picking (use 3 product price 3, 1 product price 5)
        move_serial = picking_assigned.move_lines.filtered(lambda move: move.product_qty == 4)
        move_lot = picking_assigned.move_lines - move_serial
        
        move_serial.move_line_ids[0].lot_id = in_move_serial_2.move_line_ids[0].lot_id
        move_serial.move_line_ids[1].lot_id = in_move_serial_2.move_line_ids[1].lot_id
        move_serial.move_line_ids[2].lot_id = in_move_serial_2.move_line_ids[2].lot_id
        
        move_lot.move_line_ids.lot_id = in_move_lot_2.move_line_ids.lot_id
        
        first_result = picking_assigned.button_validate()
        self.env[first_result['res_model']].browse(first_result['res_id']).process()

        self.assertEqual(picking_waiting.state, 'assigned')
        self.assertEqual(picking_assigned.state, 'done')

        # Validate second stock picking
        second_result = picking_waiting.button_validate()
        self.env[first_result['res_model']].browse(second_result['res_id']).process()

        self.assertEqual(picking_waiting.state, 'done')
        self.assertEqual(picking_assigned.state, 'done')

        # The cost of product should be (serial: 3*3 + 1*5 = 14) + (lot: 5 * 250 = 1250) = 1264
        self.assertEqual(len(picking_assigned.account_move_ids), 5)
        self.assertEqual(len(picking_waiting.account_move_ids), 5)
        self.assertEqual(sum(picking_assigned.account_move_ids.mapped('amount_total')), 1264)
        self.assertEqual(sum(picking_waiting.account_move_ids.mapped('amount_total')), 1264)

        # Account move lines of Picking Assigned
        pa_aml_from_wh = picking_assigned.account_move_line_ids.filtered(lambda aml: aml.balance < 0)
        pa_aml_to_transit = picking_assigned.account_move_line_ids - pa_aml_from_wh

        # Account move lines of Picking Waiting
        pw_aml_from_transit = picking_waiting.account_move_line_ids.filtered(lambda aml: aml.balance < 0)
        pw_aml_to_sub_wh = picking_waiting.account_move_line_ids - pw_aml_from_transit

        self.assertEqual(sum(pa_aml_from_wh.mapped('credit')), 1264)
        self.assertEqual(sum(pa_aml_to_transit.mapped('debit')), 1264)

        self.assertEqual(sum(pw_aml_from_transit.mapped('credit')), 1264)
        self.assertEqual(sum(pw_aml_to_sub_wh.mapped('debit')), 1264)
        
        self.assertEqual(product_1.standard_price, 0)
        self.assertEqual(product_2.standard_price, 0)
