from odoo.tests.common import tagged
from odoo.exceptions import AccessError
from odoo import fields
from dateutil.relativedelta import relativedelta

from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):

    #Case 1
    def test_insurance_type_fleet_group_user_access_right(self):
        """
        INPUT: User in group 'Fleet / User'
        OUTPUT: Can read information of insurance type
                Can not create, write, unlink information of insurance type
        """
        self.insurance_type_public_liability_insurance.with_user(self.fleet_group_user).read()
        with self.assertRaises(AccessError):
            self.env['fleet.insurance.type'].with_user(self.fleet_group_user).create({
                'name': 'Insurance type test',
                'period': 10,
                'days_to_notify': 5
            })
        with self.assertRaises(AccessError):
            self.insurance_type_public_liability_insurance.with_user(self.fleet_group_user).write({
                'period': 12
            })
        with self.assertRaises(AccessError):
            self.insurance_type_public_liability_insurance.with_user(self.fleet_group_user).unlink()

    #Case 3
    def test_vehicle_insurance_fleet_group_user_access_right(self):
        """
        INPUT: User in group 'Fleet / User'
        OUTPUT: Can read information of Vehicle Insurance
                Can not create, write, unlink information of Vehicle Insurance
        """
        self.vehicle_insurance.with_user(self.fleet_group_user).read()

        with self.assertRaises(AccessError):
            self.env['fleet.vehicle.insurance'].with_user(self.fleet_group_user).create({
                'name': 'Vehicle Insurance for vehicle A',
                'vehicle_id': self.vehicle_a.id,
                'fleet_insurance_type_id': self.insurance_type_public_liability_insurance.id,
                'date_start': fields.Date.today() + relativedelta(days=-15),
                'date_end': fields.Date.today() + relativedelta(days=-2),
                'days_to_notify': 7
            })
        with self.assertRaises(AccessError):
            self.vehicle_insurance.with_user(self.fleet_group_user).write({
                'name': 'test_access_right'
            })
        with self.assertRaises(AccessError):
            self.vehicle_insurance.with_user(self.fleet_group_user).unlink()
