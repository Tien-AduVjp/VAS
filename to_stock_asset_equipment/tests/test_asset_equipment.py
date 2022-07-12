from datetime import datetime

from odoo.tests import Form
from odoo.exceptions import UserError, QWebException

from odoo.addons.to_stock_asset.tests.stock_asset_common import TestStockAssetCommon


class TestAssetEquipment(TestStockAssetCommon):
    
    @classmethod
    def setUpClass(cls):
        super(TestAssetEquipment, cls).setUpClass()
        
        cls.lot1 = cls.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': cls.product1.id,
            'company_id': cls.env.company.id,
        })
        cls.lot2 = cls.env['stock.production.lot'].create({
            'name': 'lot2',
            'product_id': cls.product1.id,
            'company_id': cls.env.company.id,
        })
        
        # Create data asset, lot, equipment
        cls.product1.can_be_equipment = True
        cls.picking_type_in._update_buy_picking_types()
        # receive 2 units @ 100.000.000 per unitv
        picking1 = cls._make_in_picking_with_serial_product_equipment(cls, 
                                                             cls.product1,
                                                             2,
                                                             100000000,
                                                             serials=['ASSET_001', 'ASSET_002']
                                                             )
        # out 1 units @ 100.000.000 per unit with serial as ASSET_001
        cls.picking2 = cls._make_out_picking_as_asset(cls, cls.product1, 1)
        cls._force_serial_on_move_line(cls, cls.picking2.move_line_ids, 'ASSET_001')
        cls._validate_picking(cls, cls.picking2)

        cls.asset = cls._search_asset_is_in_draft(cls, cls.picking2.move_line_ids.lot_id)
        cls.equipment = cls.asset.equipment_id
        cls.lot = cls.asset.production_lot_id
        
        # Recompute asset line to possible done(close) asset
        cls.asset.write({
            'method_number': 1,
            'method_period': 1,
            'method_time': 'number',
            'date_first_depreciation': 'manual',
            'prorata': False,
            'first_depreciation_date': datetime.now(),
            'date': datetime.now()
            })
        cls.asset.action_compute_depreciation_board()        

    def _make_in_picking_with_serial_product_equipment(self, product, quantity, price_unit, serials=[]):
        """ Helper to create in picking with product that is enabled serial.
        """
        move = self.env['stock.move'].create({
            'name': 'in %s' % str(quantity),
            'product_id': product.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': quantity,
            'picking_type_id': self.picking_type_in.id,
            'price_unit': price_unit,
        })

        picking = self.env['stock.picking'].create({
            'picking_type_id': move[0].picking_type_id.id,
            'immediate_transfer': True,
            'location_id': move[0].location_id.id,
            'location_dest_id': move[0].location_dest_id.id,
            'move_lines': [(6, 0, move.ids)],
        })

        serials_length = len(serials)
        move_form = Form(move, view='stock.view_stock_move_nosuggest_operations')
        for i in range(int(move.product_uom_qty)):
            with move_form.move_line_nosuggest_ids.new() as line:
                line.lot_name = serials_length > i and serials[i] or 'sn0000%s' % self.sn_count
                line.can_create_equipment = True
                self.sn_count += 1
        move = move_form.save()

        picking.button_validate()
        return picking

    def test_constraint_asset_lot_duplicate(self):
        """ Check constraint duplicate asset confirmed per equipment"""
        asset_form = Form(self.env['account.asset.asset'])
        asset_form.category_id = self.asset_category
        asset_form.production_lot_id = self.lot1
        asset_form.save().validate()
            
        with self.assertRaises(UserError):
            asset_form = Form(self.env['account.asset.asset'])
            asset_form.category_id = self.asset_category
            asset_form.production_lot_id = self.lot1
            asset_form.save().validate()
    
    def test_state_asset_equal_state_equipment(self):
        """ Check state on asset equal on equipment"""
        # State = draft
        self.assertEqual(self.asset.state, 'draft')
        self.assertEqual(self.asset.state, self.equipment.asset_status)
        
        self.asset.validate()
        
        # State = open
        self.assertEqual(self.asset.state, 'open')
        self.assertEqual(self.asset.state, self.equipment.asset_status)

        with self.assertRaises(QWebException), self.cr.savepoint():
            self.asset.depreciation_line_ids.create_move()
            self.assertEqual(self.asset.state, 'close')
            self.assertEqual(self.asset.state, self.equipment.asset_status)
            raise QWebException('trick to rollback')

        
        with self.assertRaises(QWebException), self.cr.savepoint():
            self.env['asset.stock.in.wizard'].with_context(active_ids=[self.asset.id]) \
                                                .create({}) \
                                                .create_asset_stock_in() 
            # State = stock-in
            self.assertEqual(self.asset.state, 'stock_in')
            self.assertEqual(self.asset.state, self.equipment.asset_status)
            raise QWebException('trick to rollback')
        
        with self.assertRaises(QWebException), self.cr.savepoint():
            self.env['asset.sell.wizard'].with_context(default_asset_id=self.asset.id, 
                                                       active_ids=[self.asset.id]) \
                                                        .create({}).action_sell() 
            # State = sold
            self.assertEqual(self.asset.state, 'sold')
            self.assertEqual(self.asset.state, self.equipment.asset_status)
            raise QWebException('trick to rollback')
        
        
        self.env['asset.dispose.wizard'].with_context(default_asset_id=self.asset.id, 
                                                       active_ids=[self.asset.id]) \
                                                       .create({}).action_dispose() 
        # State = disposed     
        self.assertEqual(self.asset.state, 'disposed')
        self.assertEqual(self.asset.state, self.equipment.asset_status)
        
    def test_export_asset_to_equipment(self):
        """ Check date in stock picking equal equipment assignment date"""
        self.assertEqual(self.equipment.assign_date, self.picking2.date.date())
        
        """ Check type and value assignment on lot corresponding on equipment"""
        employee = self.env['hr.employee'].search([], limit=1)
        self.lot.write({
            'asset_assign_to':'employee',
            'employee_id': employee.id
        })
        self.assertEqual(self.equipment.equipment_assign_to, 'employee')
        self.assertEqual(self.equipment.employee_id, employee)

        department = self.env['hr.department'].search([], limit=1)
        self.lot.write({
            'asset_assign_to':'department',
            'department_id': department.id
        })
        self.assertEqual(self.equipment.equipment_assign_to, 'department')
        self.assertEqual(self.equipment.department_id, department)

        self.lot.write({
            'asset_assign_to':'other',
            'department_id': department.id,
            'employee_id': employee.id
        })
        self.assertEqual(self.equipment.equipment_assign_to, 'other')
        self.assertEqual(self.equipment.department_id, department)
        self.assertEqual(self.equipment.employee_id, employee)

    def test_two_asset_with_same_equipment(self):
        picking1 = self._make_in_picking_with_serial_product_equipment(
            self.product1,
            2,
            10000000,
            serials=['LOT_WITH_EQUIPMENT_001', 'LOT_WITH_EQUIPMENT_002'])

        picking2 = self._make_out_picking_as_asset(self.product1, 2)
        self._validate_picking(picking2)

        assets = self._search_asset_is_in_draft(picking2.move_line_ids.lot_id)

        # Case: asset 1 is in open state, asset 2 is in draft state
        # two asset with same equipment
        # Action: validate the asset 1
        equipment1 = assets[1].equipment_id
        assets[1].equipment_id = assets[0].equipment_id
        assets[0].validate()
        with self.assertRaises(UserError):
            assets[1].validate()

        # Case: two asset are in open state
        # Action: change serial of asset1 with same equipment
        assets[1].equipment_id = equipment1
        assets[1].validate()
        with self.assertRaises(UserError):
            assets[1].write({'equipment_id': assets[0].equipment_id.id})
