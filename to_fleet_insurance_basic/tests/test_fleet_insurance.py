from psycopg2 import IntegrityError

from odoo.exceptions import UserError
from odoo.tools import mute_logger
from odoo.tests.common import tagged, Form
from odoo import fields
from dateutil.relativedelta import relativedelta

from .common import Common


@tagged('post_install', '-at_install')
class TestFleetInsurance(Common):
    
    #Case 1
    def test_create_new_fleet_vehicle_insurance(self):
        """
        INPUT: Create new vehicle insurance for vehicle A
        OUTPUT: New vehicle insurance is link to Vehicle A
        """
        self.vehicle_insurance.write({
            'state':'confirmed'
        })       
        self.assertIn(self.vehicle_insurance, self.vehicle_a.current_insurance_ids)
        
    #Case 2
    def test_01_unlink_fleet_insurance(self):
        """
        INPUT: State of vehicle insurance is draft
        OUTPUT: Can delete vehicle insurance
        """
        self.vehicle_insurance.unlink()
        
    #Case 3
    def test_02_unlink_fleet_insurance(self):
        """
        INPUT: State of vehicle insurance is confirmed
        OUTPUT: Can not delete vehicle insurance
        """
        self.vehicle_insurance.write({
            'state':'confirmed'
        })
        with self.assertRaises(UserError):
            self.vehicle_insurance.unlink()
        
    #Case 4
    def test_01_write_fleet_insurance(self):
        """
        INPUT: State of vehicle insurance is draft
        OUTPUT: Can update information of vehicle insurance
        """
        vehicle_insurance_form = Form(self.vehicle_insurance)
        self.assertFalse(vehicle_insurance_form._get_modifier('name', 'readonly'))
        self.assertFalse(vehicle_insurance_form._get_modifier('vehicle_id', 'readonly'))
        self.assertFalse(vehicle_insurance_form._get_modifier('fleet_insurance_type_id', 'readonly'))
        self.assertFalse(vehicle_insurance_form._get_modifier('date_start', 'readonly'))
        self.assertFalse(vehicle_insurance_form._get_modifier('date_end', 'readonly'))
        self.assertFalse(vehicle_insurance_form._get_modifier('days_to_notify', 'readonly'))
    
    #Case 5
    def test_02_write_fleet_insurance(self):
        """
        INPUT: State of vehicle insurance is confirmed
        OUTPUT: Cannot update information of vehicle insurance except 'days to notify'
        """
        self.vehicle_insurance.write({
            'state':'confirmed'
        })
        vehicle_insurance_form = Form(self.vehicle_insurance)
        self.assertTrue(vehicle_insurance_form._get_modifier('name', 'readonly'))
        self.assertTrue(vehicle_insurance_form._get_modifier('vehicle_id', 'readonly'))
        self.assertTrue(vehicle_insurance_form._get_modifier('fleet_insurance_type_id', 'readonly'))
        self.assertTrue(vehicle_insurance_form._get_modifier('date_start', 'readonly'))
        self.assertTrue(vehicle_insurance_form._get_modifier('date_end', 'readonly'))
        self.assertFalse(vehicle_insurance_form._get_modifier('days_to_notify', 'readonly'))
        
    #Case 6
    def test_fleet_insurance_expired(self):
        """
        INPUT: State of vehicle insurance is confirmed, and vehicle insurance is expired. Run scheduled actions 'Fleet Vehicle Insurance - Set Expiry'
        OUTPUT: State of vehicle insurance is expired
        """
        self.vehicle_insurance.write({
            'state':'confirmed'
        })
        self.cron_set_expired.method_direct_trigger()
        self.assertEqual(self.vehicle_insurance.state, 'expired')
        
    #Case 7
    def test_fleet_insurance_send_expire_notice(self):
        """
        INPUT: State of vehicle insurance is confirmed, and vehicle insurance will be expired. Run scheduled actions 'Fleet Vehicle Insurance - Expiry Notification'
        OUTPUT: Get notify: The vehicle insurance will be expired
        """
        self.vehicle_insurance.write({
            'state':'confirmed',
            'date_end': fields.Date.today() + relativedelta(days=5),
        })
        self.cron_send_expire_notice.method_direct_trigger()        
        self.assertGreater(self.env['mail.compose.message'].
            search_count([('model', '=', 'fleet.vehicle.insurance'), 
                         ('res_id', '=', self.vehicle_insurance.id),
                         ('template_id', '=', self.env.ref('to_fleet_insurance_basic.email_template_fleet_vehicle_insurance_expiry_warning').id)]), 0)
        
    #Case 8
    @mute_logger('odoo.sql_db')
    def test_01_insurance_type(self):
        """
        INPUT: Delete insurance type 'Public Liability Insurance' which is link to vehicle insurance of vehicle A
        OUTPUT: Can not delete
        """
        with self.assertRaises(IntegrityError):
            self.insurance_type_public_liability_insurance.unlink()         
        
    #Case 9
    @mute_logger('odoo.sql_db')
    def test_02_insurance_type(self):
        """
        INPUT: Update 'days to notify' of insurance type 'Public Liability Insurance'. Set value -1 for 'days to notify '
        OUTPUT: Can not update
        """
        with self.assertRaises(IntegrityError):
            self.insurance_type_public_liability_insurance.write({
                'days_to_notify': -1
            })
