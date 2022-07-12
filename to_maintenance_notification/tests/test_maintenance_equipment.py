from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from . import common

@tagged('post_install','-at_install')
class TestMaintenanceEquipment(common.Common):   
   
    # -------------------------------------------Test Compute Next Requesst-----------------------------------------------#

    def test_1_1_compute_next_maintenance(self):
        """
            +)  UoM of milestone IS NOT belong category of working time.
            +)  Equipment have maintenance schedule, working frequency.
            +)  Total working amount of equipment NOT achieve to milestone.
            +)  This case will test compute next date need to request maintenance.
                Equipment already worked 10 days:
                --------------------------------------------------------------------------------------------------------
                day_amount              = working_amount / period_time
                                        = 420 / 7 = 60 (Unit Working)
                --------------------------------------------------------------------------------------------------------
                total_working_amount    = start_amount + day_amount x working_days 
                                        = 20           + 60         x 10 
                                        = 620 (Unit Working)
                --------------------------------------------------------------------------------------------------------
                days to next maintenance of milestone_800   = (milestone_800.amount - total_working_amount) / day_amount
                                                            = (800                  - 620                 ) / 60
                                                            = 3 (days)
                --------------------------------------------------------------------------------------------------------
                days to next maintenance of milestone_1000  = (milestone_1000.amount - total_working_amount) / day_amount
                                                            = (1000                  - 620                 ) / 60
                                                            = 6 (days)
                --------------------------------------------------------------------------------------------------------
                **Result of compute:
                    Nearest days to next maintenance of equipment is: to_day + 3
                              Next milestone maitenance of equipment: milestone_800
        """   
        self.equipment_test_01.update({
            'maintenance_schedule_ids':[(6,0,[self.maintenance_schedule_part_02.id,self.maintenance_schedule_part_03.id])],
            'equipment_working_frequency_ids':[(6,0,[self.equipment_working_frequency.id])]
        })
        self.assertEqual(self.equipment_test_01.next_maintenance_milestone_id,self.milestone_800)
        self.assertEqual(self.equipment_test_01.next_action_date,fields.date.today() + timedelta(days = 3))

    def test_1_2_compute_next_maintenance(self):
        """
            +)  UoM of Milestone IS NOT working_time.
            +)  Equipment have maintenance schedule, working frequency.
            +)  Total working amount of equipment exceed milestones.
            +)  Equipment already worked 10 days:
                total_working_amount    = 620 (Unit Working)    
                total working amount exceed the milestone_100(amount 100)
                => Cannot compute days to next maintenance for milestone_100
        """
        self.equipment_test_01.update({
            'maintenance_schedule_ids':[(6,0,[self.maintenance_schedule_part_01.id])],
            'equipment_working_frequency_ids':[(6,0,[self.equipment_working_frequency.id])]
        })
        self.assertFalse(self.equipment_test_01.next_maintenance_milestone_id)
        self.assertFalse(self.equipment_test_01.next_action_date)

    def test_1_3_compute_next_maintenance(self):
        """
            +)  UoM of Milestone IS NOT working_time.
            +)  Equipment have maintenance schedule, working frequency.
            +)  UoM of milestone and UoM working frequency NOT SAME each other. 
        """
        self.equipment_working_frequency.update({
            'working_uom_id':self.ref('uom.product_uom_meter')
        })
        self.equipment_test_01.update({
            'maintenance_schedule_ids':[(6,0,[self.maintenance_schedule_part_01.id])],
            'equipment_working_frequency_ids':[(6,0,[self.equipment_working_frequency.id])]
        })
        self.assertFalse(self.equipment_test_01.next_maintenance_milestone_id)
        self.assertFalse(self.equipment_test_01.next_action_date)
    
    def test_1_4_compute_next_maintenance(self):
        """
            +)  UoM of Milestone IS NOT working_time
            +)  Equipment have maintenance schedule, but NOT working frequency.
        """
        self.equipment_test_01.update({
            'maintenance_schedule_ids':[(6,0,[self.maintenance_schedule_part_01.id])]           
        })
        self.assertFalse(self.equipment_test_01.next_maintenance_milestone_id)
        self.assertFalse(self.equipment_test_01.next_action_date)

    def test_2_1_compute_next_maintenance(self):
        """
            +)  UoM milestone belong category of working time.
            +)  Equipment have maintenance schedule.
            +)  Equipment already worked 10 days (8 hours / day)
                ----------------------------------------------------------------------------------------------------------------------------
                total_working_hours =   10 * 8 = 80 (hours)
                ----------------------------------------------------------------------------------------------------------------------------
                days to next maintenance milestone_by_hours_100 = (milestone_by_hours_100.amount - total_working_hours) / working_hour_a_day
                                                                = (100                           - 80                 ) / 8                
                                                                =  2.5 (days)
                ----------------------------------------------------------------------------------------------------------------------------
                **Result of compute:
                    Nearest days to next maintenance of equipment is: to_day + 2
                              Next milestone maitenance of equipment: milestone_by_hours_100
        """
        self.equipment_test_01.update({
            'maintenance_schedule_ids':[(6,0,[self.maintenance_schedule_part_02.id,self.maintenance_schedule_part_04.id])],            
        })    
        self.assertEqual( self.equipment_test_01.next_maintenance_milestone_id,self.milestone_by_hours_100)
        self.assertEqual(self.equipment_test_01.next_action_date,fields.date.today() + timedelta(days = 2))

    
    # -------------------------------------------Test Cron Generate Next Request-----------------------------------------------#

    def _get_equipment_next_request(self):
        return self.env['maintenance.request'].search([('stage_id.done', '=', False),
                                                    ('equipment_id', '=', self.equipment_test_01.id),
                                                    ('company_id', '=', self.env.company.id),
                                                    ('maintenance_type', '=', 'preventive')])

    def test_01_cron_generate_requests(self): 
        """
            Cannot auto generate maintenance request for equipment, which is not setting working frequency and maintenance schedule.
        """
        self.env.ref('maintenance.maintenance_requests_cron').method_direct_trigger()     
        self.assertFalse(self._get_equipment_next_request())
    
    def test_02_cron_generate_requests(self):
        """
            Equipment was setup with working frequency, maintenance schedule, 
            and can compute next action date should be auto generate maintenance request.
        """
        self.equipment_test_01.update({
            'maintenance_schedule_ids':[(6,0,[self.maintenance_schedule_part_03.id])],
            'equipment_working_frequency_ids':[(6,0,[self.equipment_working_frequency.id])]})      
        self.env.ref('maintenance.maintenance_requests_cron').method_direct_trigger()        
        self.assertTrue(len(self._get_equipment_next_request()) == 1\
             and self._get_equipment_next_request().request_date == self.equipment_test_01.next_action_date) 
        # if equipment already have a maintenance request is open, NOT recompute next maintenance and create new request maintenance.
        self.equipment_test_01.update({
            'maintenance_schedule_ids':[(6,0,[self.maintenance_schedule_part_02.id,self.maintenance_schedule_part_03.id])],
            'equipment_working_frequency_ids':[(6,0,[self.equipment_working_frequency.id])]})         
        self.env.ref('maintenance.maintenance_requests_cron').method_direct_trigger()
        self.assertTrue(len(self._get_equipment_next_request()) == 1\
             and self._get_equipment_next_request().request_date == self.equipment_test_01.next_action_date)
