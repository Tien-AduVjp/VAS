from odoo.tests import SavepointCase


class TestCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # waypoint address_id
        cls.address_hn = cls.env['res.partner'].create({
            'name': 'Ha Noi',
            'street': 'Street 01',
            'street2': 'Street 02',
            'city': 'Ha Noi',
            'state_id': cls.env.ref('base.state_vn_VN-HN').id
        })
        cls.address_hp = cls.env['res.partner'].create({
            'name': 'Hai Phong',
            'street': 'Street 01',
            'street2': 'Street 02',
            'city': 'Hai Phong',
            'state_id': cls.env.ref('base.state_vn_VN-HP').id
        })
        cls.address_qn = cls.env['res.partner'].create({
            'name': 'Hai Phong',
            'street': 'Street 01',
            'street2': 'Street 02',
            'city': 'Hai Phong',
            'state_id': cls.env.ref('base.state_vn_VN-13').id
        })
        # routes
        cls.route = cls.env['route.route'].create({
            'name': 'Route test'
        })
        # waypoints
        cls.waypoint_hn = cls.env['route.waypoint'].create({
            'address_id': cls.address_hn.id,
            'route_id': cls.route.id
        })
        cls.waypoint_hp = cls.env['route.waypoint'].create({
            'address_id': cls.address_hp.id,
            'route_id': cls.route.id
        })
        cls.waypoint_qn = cls.env['route.waypoint'].create({
            'address_id': cls.address_qn.id,
            'route_id': cls.route.id
        })

        cls.waypoint_area = cls.env['route.waypoint.area'].create({
            'name': 'Waypoint Area',
            'restricted_by': 'none'
        })

