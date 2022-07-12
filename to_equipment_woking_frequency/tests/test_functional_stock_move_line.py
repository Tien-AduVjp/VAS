from odoo import fields
from odoo.tests import TransactionCase, tagged

from . import ultils


@tagged('post_install', '-at_install')
class TestMaintenanceEquipment(TransactionCase):
    
    def setUp(self):
        super(TestMaintenanceEquipment, self).setUp()
        self.ProductObj = self.env['product.product']   
        self.picking_type_in_id = self.ref('stock.picking_type_in')
        self.supplier_location_id = self.ref('stock.stock_location_suppliers')
        self.stock_location_id = self.ref('stock.stock_location_stock')  
        self.uom_unit_id = self.ref('uom.product_uom_unit')  
        self.day_uom_id = self.ref('uom.product_uom_day') 
        self.lot_name = 'sn-test-0000111'      
        # setup equipment frequency
        self.working_frequence_template = self.env['working.frequency.template'].create({
            'working_amount':ultils.START_AMOUNT,
            'working_uom_id':self.uom_unit_id,
            'period_time':ultils.PERIOD_TIME,
            'period_time_uom_id':self.day_uom_id
        })
        # Setup stock move data     
        self.product = self.ProductObj.create({
            'name':'Test Produc Equipment',
            'type':'product',
            'can_be_equipment':True,
            'tracking':'serial',
            'working_frequency_template_ids':[(6, 0, [self.working_frequence_template.id])]
        })
        self.stock_picking_in = self.env['stock.picking'].create({
            'picking_type_id':self.picking_type_in_id,
            'location_id':self.stock_location_id,
            'location_dest_id': self.supplier_location_id
        })
        self.stock_move = self.env['stock.move'].create({
            'name':'stock_move',
            'product_id':self.product.id,
            'picking_id':self.stock_picking_in.id,
            'location_id':self.stock_location_id,
            'location_dest_id': self.supplier_location_id,
            'product_uom': self.uom_unit_id        
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
            'location_id':self.stock_move.location_id.id,
            'location_dest_id':self.stock_move.location_dest_id.id,
            'lot_id':self.production_lot.id,
            'can_create_equipment':True
        })
        self.stock_picking_in.action_done()  
        self.equipment = self.env['maintenance.equipment'].search([('serial_no', 'ilike', self.lot_name)])   
        
    def test_create_equipment_with_working_frequency_when_stock_move(self):
        """
            Equipment with working frequency should be created when stock move done.
        """
        compare = self.equipment.equipment_working_frequency_ids\
                and self.equipment.effective_date == fields.Date.today()\
                and self.product.working_frequency_template_ids.working_amount == self.equipment.equipment_working_frequency_ids.working_amount\
                and self.product.working_frequency_template_ids.working_uom_id == self.equipment.equipment_working_frequency_ids.working_uom_id\
                and self.product.working_frequency_template_ids.period_time == self.equipment.equipment_working_frequency_ids.period_time\
                and self.product.working_frequency_template_ids.period_time_uom_id == self.equipment.equipment_working_frequency_ids.period_time_uom_id
        self.assertTrue(compare, "Product and correlative equipment must have same working frequency")
