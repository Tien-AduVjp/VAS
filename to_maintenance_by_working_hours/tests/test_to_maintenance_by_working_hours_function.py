from odoo import fields
from odoo.tests import tagged
from odoo.tools.misc import mute_logger
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta
import logging

from unittest.mock import patch

try:
    # try to use UniqueViolation if psycopg2's version >= 2.8
    from psycopg2 import errors
    CheckViolation = errors.CheckViolation
except Exception:
    import psycopg2
    CheckViolation = psycopg2.IntegrityError

from .test_to_maintenance_by_working_hours_common import TestMaintenanceWorkingHoursCommon


@tagged('post_install','-at_install')
class TestMaintenanceWorkingHoursFunction(TestMaintenanceWorkingHoursCommon):
# Test functional
    """ 
        Case 1 + 2: Check _sql_constraints on field 'ave_daily_working_hours > 0' 
                    and 'working_hour_period > 0' on the Equipment.   
    """
    @mute_logger('odoo.sql_db')
    def test_01_daily_working_hour_can_not_negative(self):
        equipment1 = self.equipment.create({
            'name': 'Mac Book',
            'ave_daily_working_hours': 8,
            'working_hour_period': 80, 
            'maintenance_team_id': self.maintenance_team.id
            })
        
        with self.assertRaises(CheckViolation):
            self._update_equipment(equipment1,-1, 80)
            
    @mute_logger('odoo.sql_db')
    def test_02_working_hour_period_can_not_negative(self):
        equipment1 = self.equipment.create({
            'name': 'Mac Book',
            'ave_daily_working_hours': 8,
            'working_hour_period': 80, 
            'maintenance_team_id': self.maintenance_team.id
            })
        
        with self.assertRaises(CheckViolation):
            self._update_equipment(equipment1,8, -80)
            
    """ 
        Case 3: 
            1. Edit 'ave_daily_working_hours' and 'working_hour_period' on the Equipment.
            2. The Equipment have no maintenance request.
            3. Check next preventive maintenance preventive day
                    
    """
    @patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2021-10-14'))
    @patch.object(fields.Date, 'context_today', lambda *arg, **kwarg: fields.Date.to_date('2021-10-14'))
    def test_03_edit_working_hour_of_equipment_without_request(self):
        self._update_equipment(self.hp_laptop, 8, 80)
        next_action_date = fields.Date.today() + timedelta(days=10)
        self.assertEqual(
            self.hp_laptop.next_action_date, 
            next_action_date, 
            "Error testing: next action date not equal to current date + 10"
            )
    
    """ 
        Case 4: 
            1. Create a maintenance request with request date 30 days in the future
            2. Check next preventive maintenance preventive day
     
    """
    @patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2021-10-14'))
    @patch.object(fields.Date, 'context_today', lambda *arg, **kwarg: fields.Date.to_date('2021-10-14'))
    def test_04_create_a_maintenance_todo_request(self):
        self.maintenance_request_todo.update({
            'name': 'Maintenance request for HP Laptop',
            'equipment_id': self.hp_laptop.id,
            'request_date': fields.Date.to_date('2021-11-14'),
            'maintenance_type': 'preventive'
            })
        self._update_equipment(self.hp_laptop, 8, 81)
        next_action_date = fields.Date.today() + timedelta(days=10)
        
        self.assertEqual(
            self.hp_laptop.next_action_date, 
            next_action_date, 
            "Error testing: next action date not equal to current date + 10"
            )
        self.hp_laptop._cron_generate_requests()
        
        self.assertEqual(
            self.hp_laptop.maintenance_count, 
            2, 
            "Error testing: no maintenance request automatically created"
            )

    """ 
        Case 5: 
            1. Create a maintenance request with request date and close date 30 days in the past
            2. Check next preventive maintenance preventive day
     
    """
    @patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2021-10-14'))
    @patch.object(fields.Date, 'context_today', lambda *arg, **kwarg: fields.Date.to_date('2021-10-14'))
    def test_05_create_a_maintenance_done_request(self):
        self.maintenance_request_done.stage_id.done =True
        self.maintenance_request_done.update({
            'name': 'Maintenance request for HP Laptop',
            'equipment_id': self.hp_laptop.id,
            'request_date': fields.Date.to_date('2021-9-14'),
            'maintenance_type': 'preventive',
            'close_date': fields.Date.to_date('2021-9-14')
            })
        next_action_date = fields.Date.today()
        self._update_equipment(self.hp_laptop, 8, 80)
        self.assertEqual(
            self.hp_laptop.next_action_date, 
            next_action_date, 
            "Error testing: next action date not equal to current date"
            )
        self.hp_laptop._cron_generate_requests()
        self.assertEqual(
            self.hp_laptop.maintenance_count, 
            2, 
            "Error testing: no maintenance request automatically created"
            )

    """ 
        Case 6: 
            1. Create a maintenance request with request date and close date at current date
            2. Check next preventive maintenance preventive day
     
    """
    @patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2021-10-14'))
    @patch.object(fields.Date, 'context_today', lambda *arg, **kwarg: fields.Date.to_date('2021-10-14'))
    def test_06_create_a_maintenance_done_request(self):
        self.maintenance_request_done.stage_id.done =True
        self.maintenance_request_done.update({
            'name': 'Maintenance request for HP Laptop',
            'equipment_id': self.hp_laptop.id,
            'request_date': fields.Date.to_date('2021-10-14'),
            'maintenance_type': 'preventive',
            'close_date': fields.Date.to_date('2021-10-14')
            })
        next_action_date = fields.Date.today() + timedelta(days=10)
        self._update_equipment(self.hp_laptop, 8, 80)
        self.assertEqual(
            self.hp_laptop.next_action_date, 
            next_action_date, 
            "Error testing: next action date not equal to current date + 10"
            )
        self.hp_laptop._cron_generate_requests()
        self.assertEqual(
            self.hp_laptop.maintenance_count, 
            2, 
            "Error testing: no maintenance request automatically created"
            )

    """ 
        Case 7: 
            1. Create a maintenance request with request date and close date 45 days in the past
            2. Create a maintenance request with request date is current date
            3. Check next preventive maintenance preventive day     
    """ 
    @patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2021-10-14'))
    @patch.object(fields.Date, 'context_today', lambda *arg, **kwarg: fields.Date.to_date('2021-10-14'))
    def test_07_create_02_maintenance_todo_and_done_request(self):
        self.maintenance_request_done.stage_id.done =True
        self.maintenance_request_done.update({
            'name': 'Maintenance request 1 for HP Laptop',
            'equipment_id': self.hp_laptop.id,
            'request_date': fields.Date.to_date('2021-9-1'),
            'maintenance_type': 'preventive',
            'close_date': fields.Date.to_date('2021-9-1')
            })
        
        self.maintenance_request_todo.update({
            'name': 'Maintenance request 2 for HP Laptop',
            'equipment_id': self.hp_laptop.id,
            'request_date': fields.Date.to_date('2021-10-15'),
            'maintenance_type': 'preventive',
            })
        
        next_action_date = fields.Date.today()
        self._update_equipment(self.hp_laptop, 8, 81)
        self.assertEqual(
            self.hp_laptop.next_action_date, 
            next_action_date, 
            "Error testing: next action date not equal to current date"
            )
        self.hp_laptop._cron_generate_requests()
        self.assertEqual(
            self.hp_laptop.maintenance_count, 
            3, 
            "Error testing: no maintenance request automatically created"
            )

    """ 
        Case 8: 
            1. Create a maintenance request with request date and close date are current date
            2. Create a maintenance request with request date 3 days in the future
            3. Check next preventive maintenance preventive day     
    """ 
    @patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2021-10-14'))
    @patch.object(fields.Date, 'context_today', lambda *arg, **kwarg: fields.Date.to_date('2021-10-14'))
    def test_08_create_02_maintenance_todo_and_done_request(self):
        self.maintenance_request_done.stage_id.done =True
        self.maintenance_request_done.update({
            'name': 'Maintenance request 1 for HP Laptop',
            'equipment_id': self.hp_laptop.id,
            'request_date': fields.Date.to_date('2021-10-14'),
            'maintenance_type': 'preventive',
            'close_date': fields.Date.to_date('2021-10-14')
            })
        
        self.maintenance_request_todo.update({
            'name': 'Maintenance request 2 for HP Laptop',
            'equipment_id': self.hp_laptop.id,
            'request_date': fields.Date.to_date('2021-10-17'),
            'maintenance_type': 'preventive',
            })
        
        next_action_date = self.maintenance_request_done.close_date + timedelta(days = 1)
        self._update_equipment(self.hp_laptop, 8, 8)
        self.assertEqual(
            self.hp_laptop.next_action_date, 
            next_action_date, 
            "Error testing: next action date not equal to current date + 1"
            )
        self.hp_laptop._cron_generate_requests()
        self.assertEqual(
            self.hp_laptop.maintenance_count, 
            3, 
            "Error testing: no maintenance request automatically created"
            )
        

