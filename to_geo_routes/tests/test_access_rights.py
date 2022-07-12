from odoo.tests import tagged
from odoo.exceptions import AccessError

from .common import TestCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestRoutes(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestRoutes, cls).setUpClass()
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.user_demo.groups_id = [(6, 0, [cls.env.ref('to_geo_routes.group_user').id])]
        cls.user_geo_admin = cls.env.ref('base.user_admin')
        cls.user_geo_admin.groups_id = [(6, 0, [cls.env.ref('to_geo_routes.group_manager').id])]

    # GEO USER
    def test_geo_user_access_route(self):
        route = self.env['route.route'].with_user(self.user_demo).create({
            'name': 'Route test'
        })
        route.action_confirm()
        route.action_cancel()
        route.name = 'Route Test -'

        with self.assertRaises(AccessError):
            route.unlink()

    def test_geo_user_access_waypoint(self):
        route = self.env['route.route'].with_user(self.user_demo).create({
            'name': 'Route test'
        })
        waypoint = self.env['route.waypoint'].with_user(self.user_demo).create({
            'address_id': self.address_hn.id,
            'route_id': route.id
        })
        waypoint.read(['address_id'])
        waypoint.address_id = self.address_qn.id,
        waypoint.unlink()

    def test_geo_user_access_route_section(self):
        route_section = self.env['route.section'].with_user(self.user_demo).create({
            'address_from_id': self.address_hn.id,
            'address_to_id': self.address_hn.id,
            'distance': 100,
            'ave_speed': 75
        })
        route_section.read(['address_from_id'])
        route_section.distance = 1000
        route_section.unlink()

    def test_geo_user_access_route_section_line(self):
        route_section_line = self.env['route.section.line'].with_user(self.user_demo).create({
            'route_id': self.route.id,
            'address_from_id': self.address_hn.id,
            'address_to_id': self.address_qn.id,
        })
        route_section_line.read(['address_to_id'])
        route_section_line.address_from_id = self.address_hp.id
        route_section_line.unlink()

    def test_geo_user_access_waypoint_area(self):
        waypoint_area = self.env['route.waypoint.area'].with_user(self.user_demo).create({
            'name': 'Area test',
            'restricted_by': 'state'
        })
        waypoint_area.restricted_by = 'country'
        waypoint_area.unlink()

    # GEO ADMIN

    def test_geo_admin_access_route(self):
        self.assertIn(self.env.ref('to_geo_routes.group_user'), self.env.ref('to_geo_routes.group_manager').implied_ids)
        route = self.env['route.route'].with_user(self.user_geo_admin).create({
            'name': 'Route test'
        })
        route.unlink()
