from odoo.tests.common import tagged, Form
from odoo.exceptions import AccessError
from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):

    def test_multiple_companies(self):
        # case 12:
        """ Test: record revenue from vehicle trip, multiple companies.
            Input: User B - company B record revenue from a trip with company A's vehicle
            Output: record revenue failed.
        """
        self.user_admin.write({
            'groups_id': [(6, 0, self.env.ref('fleet.fleet_group_manager').ids)],
            'company_id': self.company2.id,
            'company_ids': self.company2
        })

        self.vehicle2.company_id = self.company1
        self.vehicle_trip1.vehicle_id = self.vehicle2
        self.vehicle_trip1.with_user(self.user_admin).read()

        with self.assertRaises(AccessError):
            self.record_revenue_from_trip(self.vehicle_trip1, 1, user=self.user_admin)
