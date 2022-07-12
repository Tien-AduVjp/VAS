from odoo.exceptions import AccessError
from odoo.tests.common import tagged
from .common import FleetAccountingFleetOperationCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestFlettAccountingFleetOperationSecurity(FleetAccountingFleetOperationCommon):

    @classmethod
    def setUpClass(cls):
        super(TestFlettAccountingFleetOperationSecurity, cls).setUpClass()
        cls.trip_waypoint = cls.env['fleet.vehicle.trip.waypoint'].create({
            'trip_id': cls.trip.id,
            'address_id': cls.env.ref('base.res_partner_4').id,
            'stop_duration': cls.env.ref('base.res_partner_3').id
        })
        cls.trip_section = cls.env['fleet.vehicle.trip.section'].create({
            'trip_id': cls.trip.id,
            'address_from_id': cls.env.ref('base.res_partner_4').id,
            'address_to_id': cls.env.ref('base.res_partner_3').id,
        })

    def test_1(self):
        user = self.env.ref('base.user_demo')
        group_account_invoice = self.env.ref('account.group_account_invoice')
        user.write({'groups_id': [(6, 0, [group_account_invoice.id])]})
        self.trip_waypoint.with_user(user).read(['id'])
        with self.assertRaises(AccessError):
            self.trip_waypoint.with_user(user).write(
                {'address_id': self.env.ref('base.res_partner_3').id})

        with self.assertRaises(AccessError):
            self.trip_waypoint.with_user(user).unlink()

        with self.assertRaises(AccessError):
            self.env['fleet.vehicle.trip.waypoint'].with_user(user).create({
                'trip_id': self.trip.id,
                'address_id': self.env.ref('base.res_partner_4').id,
                'stop_duration': self.env.ref('base.res_partner_2').id
            })

        self.trip_section.with_user(user).read(['id'])
        with self.assertRaises(AccessError):
            self.trip_section.with_user(user).write(
                {'address_from_id': self.env.ref('base.res_partner_2').id})

        with self.assertRaises(AccessError):
            self.trip_waypoint.with_user(user).unlink()

        with self.assertRaises(AccessError):
            self.env['fleet.vehicle.trip.section'].with_user(user).create({
                'trip_id': self.trip.id,
                'address_from_id': self.env.ref('base.res_partner_4').id,
                'address_to_id': self.env.ref('base.res_partner_2').id
            })
