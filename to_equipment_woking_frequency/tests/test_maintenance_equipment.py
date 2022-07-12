from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError

from . import ultils


@tagged('post_install', '-at_install')
class TestMaintenanceEquipment(TransactionCase):

    def setUp(self):
        super(TestMaintenanceEquipment, self).setUp()           
        self.product_uom_kgm_id = self.ref('uom.product_uom_kgm')      
        self.product_uom_gram_id = self.ref('uom.product_uom_gram')  
        self.product_uom_meter_id = self.ref('uom.product_uom_meter')      
        self.product_uom_day_id = self.ref('uom.product_uom_day')   
        self.equipment_working_frequency_kgm = self.env['equipment.working.frequency'].create({
            'start_amount': ultils.START_AMOUNT,
            'working_amount':ultils.WORKING_AMOUNT,
            'working_uom_id': self.product_uom_kgm_id,
            'period_time':ultils.PERIOD_TIME,
            'period_time_uom_id':self.product_uom_day_id
        })
        self.equipment_working_frequency_gram_data = {
            'start_amount': ultils.START_AMOUNT,
            'working_amount':ultils.WORKING_AMOUNT,
            'working_uom_id': self.product_uom_gram_id,
            'period_time':ultils.PERIOD_TIME,
            'period_time_uom_id':self.product_uom_day_id
        }
        self.equipment_working_frequency_meter_data = {
            'start_amount': ultils.START_AMOUNT,
            'working_amount':ultils.WORKING_AMOUNT,
            'working_uom_id': self.product_uom_meter_id,
            'period_time':ultils.PERIOD_TIME,
            'period_time_uom_id':self.product_uom_day_id
        }         
        self.equipment = self.env['maintenance.equipment'].create({
            'name':'Equipment Test',
            'equipment_working_frequency_ids':[(6, 0, [self.equipment_working_frequency_kgm.id])]
        })
    
    def test_check_working_frequency_ids(self):
        """
            Check unique Unit of Measure category working frequency category in one equipment.
        """
        # Test case1:Add difference Unit of Measure category working frequency for equipment
        add_working_frequency_meter = self.equipment.write({
                'equipment_working_frequency_ids':[(0, 0, self.equipment_working_frequency_meter_data
                )]
            })
        self.assertTrue(add_working_frequency_meter, "Can add difference Unit of measure equipment")
        # Test case2:Add same Unit of Measure category working frequency in one equipment.
        with self.assertRaises(ValidationError): 
            self.equipment.update({
                'equipment_working_frequency_ids':[(0, 0, self.equipment_working_frequency_gram_data
                )]
            })
