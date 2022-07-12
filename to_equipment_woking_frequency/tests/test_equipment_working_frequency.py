from datetime  import timedelta

from odoo import fields
from odoo.tests import TransactionCase, Form, tagged

from . import ultils

@tagged('post_install', '-at_install')
class TestEquipmentWorkingFrequency(TransactionCase):
    
    def setUp(self):
        super(TestEquipmentWorkingFrequency, self).setUp()
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.uom_categ_wtime = self.ref('uom.uom_categ_wtime')
        self.period_time_uom = self.env['uom.uom'].create({
            'name':'Time Working In Day',
            'category_id':self.uom_categ_wtime,
            'uom_type':'smaller',
            'factor':ultils.UOM_UNIT_RATIO
        })        
        self.form_maintenance_equipment = Form(self.env['maintenance.equipment'])
        with self.form_maintenance_equipment as f:
            f.name = 'Equipment test 01'
            f.effective_date = fields.date.today() - timedelta(days=ultils.DELTA_DAY)
            with f.equipment_working_frequency_ids.new() as line:
                line.start_amount = ultils.START_AMOUNT
                line.working_amount = ultils.WORKING_AMOUNT
                line.working_uom_id = self.uom_unit
                line.period_time = ultils.PERIOD_TIME
                line.period_time_uom_id = self.period_time_uom  
        self.form_maintenance_equipment.save()  

    def test_compute_total_working_amount(self):
        """
            *Test compute Total Working Amount
                Testcase 1: Effective date in past:
                    total_working_amount = start_amount + (working_amount / period_time) * uom_unit_ratio * delta_day
                Testcase 2: Effective date is current day or future day:
                    total_working_amount = start_amount
        """
        # test total working amount when effective date in past.
        total_working_amount = lambda: self.form_maintenance_equipment.equipment_working_frequency_ids._records[0]['total_working_amount']
        self.assertEqual(total_working_amount(), ultils.TOTAL_WORKING_AMOUNT)
        # test total working amount when effective date is current day.    
        with self.form_maintenance_equipment as f:
            f.effective_date = fields.date.today()           
        self.assertEqual(total_working_amount(), ultils.START_AMOUNT)
        # test total working amount when effective date is future day.
        with self.form_maintenance_equipment as f:
            f.effective_date = fields.date.today() + timedelta(days=ultils.DELTA_DAY)
        self.assertEqual(total_working_amount(), ultils.START_AMOUNT)     

    def test_inverse_set_total_working_amount(self):
        """
            *Test compute value of working amount when change value of total working amount.
                Testcase 1: Effective date in past:
                    working_amount = (total_working_amount - start_amount) * period_time / (uom_unit_ratio * delta_day)
                Testcase 2: Effective date is current date: working amount not change
                Testcase 2: Effective date is future date: working amount not change
                Testcase 4: Total working amount is smaller than start amount: working amount not change                    
        """
        working_amount = lambda: self.form_maintenance_equipment.equipment_working_frequency_ids._records[0]['working_amount']
        with self.form_maintenance_equipment as f:
            with f.equipment_working_frequency_ids.edit(0) as line:
                line.total_working_amount = ultils.PRE_TOTAL_WORKING_AMOUNT  
        # test inverse total working amount when effective date in past
        new_working_amount = working_amount()
        self.assertEqual(new_working_amount, ultils.INV_WORKING_AMOUNT) 
        # test inverse total working amount when effective date is current date        
        with self.form_maintenance_equipment as f:
            f.effective_date = fields.date.today()    
            with f.equipment_working_frequency_ids.edit(0) as line:
                line.total_working_amount = ultils.PRE_TOTAL_WORKING_AMOUNT        
        self.assertEqual(working_amount(), new_working_amount) 
        # test inverse total working amount when effective date is future date   
        with self.form_maintenance_equipment as f:
            f.effective_date = fields.date.today() + timedelta(days=ultils.DELTA_DAY)  
            with f.equipment_working_frequency_ids.edit(0) as line:
                line.total_working_amount = ultils.PRE_TOTAL_WORKING_AMOUNT
        self.assertEqual(working_amount(), new_working_amount) 
        # test inverse total working amount when value of total working amount is smaller than start amount
        with self.form_maintenance_equipment as f:
            with f.equipment_working_frequency_ids.edit(0) as line:
                line.total_working_amount = ultils.START_AMOUNT - 0.1
        self.assertEqual(working_amount(), new_working_amount)
