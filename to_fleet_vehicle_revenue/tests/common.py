from odoo.tests.common import SavepointCase


class Common(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.fleet_vehicle_revenue_1 = cls.env['fleet.vehicle.revenue'].create({
            'vehicle_id': cls.env.ref('fleet.vehicle_1').id
        })
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.user_demo.groups_id = [(6, 0, [cls.env.ref('to_fleet_vehicle_revenue.fleet_vehicle_revenue_group_read').id])]
