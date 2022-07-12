from odoo.tests import TransactionCase
from odoo.exceptions import AccessError


class TestEquipmentMaintenanceSchedule(TransactionCase):

    def setUp(self):
        super(TestEquipmentMaintenanceSchedule, self).setUp()
        self.picking_type_in_id = self.ref('stock.picking_type_in')
        self.supplier_location_id = self.ref('stock.stock_location_suppliers')
        self.stock_location_id = self.ref('stock.stock_location_stock')
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.lot_name = 'sn-test-00001'
        self.categ_unit = self.env['uom.category'].create({
            'name':'Unit Test Category'
        })
        self.uom_unit_test = self.env['uom.uom'].create({
            'name':'Unit Test',
            'category_id':self.categ_unit.id,
            'uom_type':'reference'
        })
        #Setup maintenance schedule data.
        self.product_milestone_10 = self.env['product.milestone'].create({
            'name':'Milestone 10 Unit',
            'amount':10,
            'uom_id':self.uom_unit_test.id
        })
        self.product_milestone_100 = self.env['product.milestone'].create({
            'name':'Milestone 100 Unit',
            'amount':100,
            'uom_id':self.uom_unit_test.id
        })
        self.product_milestone_1000 = self.env['product.milestone'].create({
            'name':'Milestone 1000 Unit',
            'amount':1000,
            'uom_id':self.uom_unit_test.id
        })
        self.product_service = self.env['product.product'].create({
            'name':'Maintenance Product Service',
            'type':'service'
        })
        self.maintenance_action = self.env['maintenance.action'].create({
            'name':'Maintenance Action',
            'service_id':self.product_service.id
        })
        self.maintenance_schedule_milestone_10 = self.env['maintenance.schedule'].create({
            'part':'Part Maintenance Demo',
            'product_milestone_id':self.product_milestone_10.id,
            'maintenance_action_id':self.maintenance_action.id
        })
        self.maintenance_schedule_milestone_100 = self.env['maintenance.schedule'].create({
            'part':'Part Maintenance Demo',
            'product_milestone_id':self.product_milestone_100.id,
            'maintenance_action_id':self.maintenance_action.id
        })
        self.maintenance_schedule_milestone_1000 = self.env['maintenance.schedule'].create({
            'part':'Part Maintenance Demo',
            'product_milestone_id':self.product_milestone_1000.id,
            'maintenance_action_id':self.maintenance_action.id
        })

        #Setup stock move data
        self.product = self.env['product.product'].create({
            'name':'Test Produc Equipment',
            'type':'product',
            'can_be_equipment':True,
            'tracking':'serial',
            'maintenance_schedule_ids':[
                (6,0,[
                    self.maintenance_schedule_milestone_10.id,
                    self.maintenance_schedule_milestone_100.id,
                    self.maintenance_schedule_milestone_1000.id
                ])
            ]
        })
        self.stock_picking_in = self.env['stock.picking'].create({
            'picking_type_id':self.picking_type_in_id,
            'location_id':self.stock_location_id,
            'location_dest_id': self.supplier_location_id
        })
        self.stock_move =  self.env['stock.move'].create({
            'name':'stock_move',
            'product_id':self.product.id,
            'picking_id':self.stock_picking_in.id,
            'location_id':self.stock_location_id,
            'location_dest_id': self.supplier_location_id,
            'product_uom': self.uom_unit.id
        })
        self.stock_picking_in.action_confirm()
        self.production_lot = self.env['stock.production.lot'].create({
            'name': self.lot_name,
            'product_id': self.product.id,
            'company_id': self.env.company.id,
        })
        self.stock_move_line = self.env['stock.move.line'].create({
            'move_id': self.stock_move.id,
            'picking_id':self.stock_picking_in.id,
            'product_id': self.product.id,
            'qty_done': 1,
            'product_uom_id':self.stock_move.product_uom.id,
            'location_id': self.stock_move.location_id.id,
            'location_dest_id': self.stock_move.location_dest_id.id,
            'lot_id':self.production_lot.id,
            'can_create_equipment':True
        })
        self.stock_picking_in.button_validate()
        self.equipment = self.env['maintenance.equipment'].search([('serial_no','ilike',self.lot_name)])
        self.lot_serial = self.env['stock.production.lot'].search([('equipment_id','=',self.equipment.id)])

    def test_sync_maintenance_schedule_equipment_when_move_stock_done(self):
        """
            Test case 1: maintenance schedule of equipment should be created and equal maintenance schedule of product / lot serial
            when move stock of product done.
        """
        self.assertEqual(self.product.maintenance_schedule_ids,self.equipment.maintenance_schedule_ids,
        "Product and correlative equipment must be same maintenance schedule")
        self.assertEqual(self.equipment.maintenance_schedule_ids,self.lot_serial.maintenance_schedule_ids,
        "Lot serial and correlative equipment must be same maintenance schedule")

    def test_maintenance_schedule_equipment_when_update_product_maintenance_schedule(self):
        """
            Test case 2: when add/remove maintenance schedule of product then maintenance schedule of correlative equipment NOT change.
        """
        equipment_maintenance_schedule_before_update_product = self.equipment.maintenance_schedule_ids
        self.product.update({
            'maintenance_schedule_ids':[(3,self.product.maintenance_schedule_ids.ids[0],0)]
        })
        self.assertEqual(self.equipment.maintenance_schedule_ids,equipment_maintenance_schedule_before_update_product,
        "Equipment maintenance schedule should not change")

    def test_maintenance_schedule_product_when_update_equipment_maintenance_schedule(self):
        """
            Test case 3: When add/remove maintenance schedule of equipment, maintenance schedule of correlative product NOT change.
            This method also test compute method: maintenance_equipment._compute_maintenance_schedule_count
        """
        self.assertEqual(self.equipment.maintenance_schedule_count,3,
        "Count maintenance schedule equipment should equal number of maintenance schedule.")
        product_maintenance_schedule_before_update_product = self.product.maintenance_schedule_ids
        self.equipment.update({
            'maintenance_schedule_ids':[(3,self.equipment.maintenance_schedule_ids.ids[0],0)]
        })
        self.assertEqual(self.product.maintenance_schedule_ids,product_maintenance_schedule_before_update_product,
        "Equipment maintenance schedule should NOT change")
        self.assertEqual(self.equipment.maintenance_schedule_count,2,
        "Count maintenance schedule equipment should equal number of maintenanece schedule.")

    def test_sync_maintenance_lot_serial_and_equipment(self):
        """
            Test case 4: When add/remove maintenance schedule of equipment/lot serial,
            maintenance schedule of correlative lot serial/equipment should change.
            This method also test compute method: stock_production_lot._compute_maintenance_schedule_count
        """
        self.assertEqual(self.lot_serial.maintenance_schedule_count,3,
        "Count maintenance schedule product lot serial should equal number of maintenance schedule.")
        self.equipment.update({
            'maintenance_schedule_ids':[(3,self.equipment.maintenance_schedule_ids.ids[0],0)]
        })
        self.assertEqual(self.equipment.maintenance_schedule_ids,self.lot_serial.maintenance_schedule_ids,
        "Lot/Serial maintenance schedule must be same with correlative equipment")
        self.lot_serial.update({
            'maintenance_schedule_ids':[(3,self.lot_serial.maintenance_schedule_ids.ids[0],0)]
        })
        self.assertEqual(self.equipment.maintenance_schedule_ids,self.lot_serial.maintenance_schedule_ids,
        "Equipment  maintenance schedule must be same with correlative lot/serial")
        self.assertEqual(self.lot_serial.maintenance_schedule_count,1,
        "Count maintenance schedule product lot serial should equal number of maintenance schedule.")

    def test_group_maintenance_user_access_right(self):
        """
            This method will test access right of maintenance user. User in group maintenance have read only access right.
        """
        self.stock_production_lot = self.env['stock.production.lot']
        self.group_maintenance_user = self.env.ref('to_product_maintenance_schedule.group_maintenance_user')
        self.maintenance_user = self.env['res.users'].create({
            'name':'Test User',
            'login':'viin_test_user',
            'email':'viin.test.user@example.viindoo.com',
            'groups_id':[(6,0,[self.group_maintenance_user.id])]
        })
        with self.assertRaises(AccessError):
            self.stock_production_lot.with_user(self.maintenance_user).create({
                'name':'0000000011',
                'product_id': self.product.id,
                'company_id': self.env.company.id
            })
        with self.assertRaises(AccessError):
            self.lot_serial.with_user(self.maintenance_user).write({
                'name':self.lot_name + '-updated'
            })
        self.env['stock.quant'].search([('lot_id','=',self.lot_serial.id)]).unlink()
        with self.assertRaises(AccessError):
            self.lot_serial.with_user(self.maintenance_user).unlink()
        self.assertTrue(self.lot_serial.with_user(self.maintenance_user).read(['id']) and True,
        "User in maintenance group should have read access right to stock.product.lot model")
