from odoo.tests.common import tagged
from odoo.exceptions import AccessError
from odoo import fields
from dateutil.relativedelta import relativedelta

from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):    
    
    #Case 1
    def test_insurance_type_internal_user_access_right(self):
        """
        INPUT: User internal
        OUTPUT: Can read information of insurance type 
                Can not create, write, unlink information of insurance type 
        """
        self.insurance_type_public_liability_insurance.with_user(self.user_internal).read()        
        with self.assertRaises(AccessError):
            self.env['fleet.insurance.type'].with_user(self.user_internal).create({
                'name': 'Insurance type test',
                'period': 10,
                'days_to_notify': 5
            })
        with self.assertRaises(AccessError):
            self.insurance_type_public_liability_insurance.with_user(self.user_internal).write({
                'period': 12
            })
        with self.assertRaises(AccessError):
            self.insurance_type_public_liability_insurance.with_user(self.user_internal).unlink()       

    #Case 2
    def test_insurance_type_fleet_group_user_access_right(self):
        """
        INPUT: User in group 'Fleet / User'
        OUTPUT: Can read, create, write, unlink information of insurance type 
        """        
        insurance_type_test = self.env['fleet.insurance.type'].with_user(self.fleet_group_user).create({
            'name': 'Insurance type test',
            'period': 10,
            'days_to_notify': 5
        })
        insurance_type_test.with_user(self.fleet_group_user).read()
        insurance_type_test.with_user(self.fleet_group_user).write({
            'period': 11
        })
        insurance_type_test.with_user(self.fleet_group_user).unlink()    
    
    #Case 3
    def test_vehicle_insurance_fleet_group_user_access_right(self):
        """
        INPUT: User in group 'Fleet / User'
        OUTPUT: Can read, create, write, unlink information of vehicle insurance 
        """
        vehicle_insurance_test = self.env['fleet.vehicle.insurance'].with_user(self.fleet_group_user).create({
            'name': 'Vehicle Insurance for vehicle B',
            'vehicle_id': self.vehicle_b.id,
            'fleet_insurance_type_id': self.insurance_type_public_liability_insurance.id,
            'date_start': fields.Date.today() + relativedelta(days=-15),
            'date_end': fields.Date.today() + relativedelta(days=5),
            'days_to_notify': 7
        })
        vehicle_insurance_test.with_user(self.fleet_group_user).read()
        vehicle_insurance_test.with_user(self.fleet_group_user).write({
            'days_to_notify': 5
        })
        vehicle_insurance_test.with_user(self.fleet_group_user).unlink()
