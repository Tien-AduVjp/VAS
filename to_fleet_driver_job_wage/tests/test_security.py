from odoo.exceptions import AccessError
from odoo.tests.common import tagged
from .common import FleetDriverJobWageCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestFleetDriverJobWageSecurity(FleetDriverJobWageCommon):

    @classmethod
    def setUpClass(cls):
        super(TestFleetDriverJobWageSecurity, cls).setUpClass()
        cls.setUP_fuel_price()

    def test_0_group_user(self):
        group_user = self.env.ref('base.group_user').id
        self.user.write({'groups_id': [(6, 0, [group_user])]})

        self.fl_fuel_price_14_10.with_user(self.user).read(['id'])

        with self.assertRaises(AccessError):
            self.fl_fuel_price_14_10.with_user(
                self.user).write({'price_per_liter': 24000})
        with self.assertRaises(AccessError):
            self.fl_fuel_price_14_10.with_user(self.user).unlink()
        with self.assertRaises(AccessError):
            self.fl_fuel_price_14_10.with_user(self.user).create({'date': "2021-10-11",
                                                                  'price_per_liter': 23000, })

        self.fl_job_wage_di_1.with_user(self.user).read(['id'])
        with self.assertRaises(AccessError):
            self.fl_job_wage_di_1.with_user(self.user).write(
                {'vehicle_id': self.env.ref('fleet.vehicle_2').id})
        with self.assertRaises(AccessError):
            self.fl_job_wage_di_1.with_user(self.user).unlink()
        with self.assertRaises(AccessError):
            self.fl_job_wage_di_1.with_user(self.user).create({
                'route_id': self.route_1.id,
                'vehicle_id': self.env.ref('fleet.vehicle_1'),
                'consumption': 50000,
                'allowance': 10000,
                'fleet_service_type_id': self.env.ref('fleet.type_service_service_1').id,
            })

    def test_1_group_account_user(self):
        group_account_user = self.env.ref('account.group_account_user').id
        # Need groupd user for add follower
        group_user = self.env.ref('base.group_user').id
        self.user.write(
            {'groups_id': [(6, 0, [group_account_user, group_user])]})

        self.fl_fuel_price_14_10.with_user(self.user).read(['id'])
        self.fl_fuel_price_14_10.with_user(
            self.user).write({'price_per_liter': 24000})
        with self.assertRaises(AccessError):
            self.fl_fuel_price_14_10.with_user(self.user).unlink()
        self.fl_fuel_price_14_10.with_user(self.user).create({'date': "2021-10-11",
                                                              'price_per_liter': 23000})

        self.fl_job_wage_di_1.with_user(self.user).read(['id'])

        self.fl_job_wage_di_1.with_user(self.user).write(
            {'vehicle_id': self.env.ref('fleet.vehicle_2').id})
        with self.assertRaises(AccessError):
            self.fl_job_wage_di_1.with_user(self.user).unlink()
        self.fl_job_wage_di_1.with_user(self.user).create({
            'route_id': self.route_1.id,
            'vehicle_id': self.env.ref('fleet.vehicle_1').id,
            'consumption': 50000,
            'allowance': 10000,
            'fleet_service_type_id': self.env.ref('fleet.type_service_service_1').id,
        })

    def test_2_group_account_manager(self):
        group_account_manager = self.env.ref('account.group_account_manager').id
        self.user.write({'groups_id': [(6, 0, [group_account_manager])]})

        self.fl_job_wage_di_1.with_user(self.user).read(['id'])

        self.fl_job_wage_di_1.with_user(self.user).write(
            {'vehicle_id': self.env.ref('fleet.vehicle_2').id})
        self.fl_job_wage_di_1.with_user(self.user).unlink()
        self.fl_job_wage_di_1.with_user(self.user).create({
            'route_id': self.route_1.id,
            'vehicle_id': self.env.ref('fleet.vehicle_1').id,
            'consumption': 50000,
            'allowance': 10000,
            'fleet_service_type_id': self.env.ref('fleet.type_service_service_1').id,
        })

        self.fl_fuel_price_14_10.with_user(self.user).read(['id'])
        self.fl_fuel_price_14_10.with_user(
            self.user).write({'price_per_liter': 24000})
        self.fl_fuel_price_14_10.with_user(self.user).unlink()
        self.fl_fuel_price_14_10.with_user(self.user).create({'date': "2021-10-11",
                                                              'price_per_liter': 23000})
