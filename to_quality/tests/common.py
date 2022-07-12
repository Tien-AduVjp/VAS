from odoo.tests.common import SavepointCase


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()

        cls.measure_type = cls.env.ref('to_quality.test_type_measure')
        cls.team = cls.env.ref('to_quality.quality_alert_team0')
        cls.quality_type = cls.env.ref('to_quality.quality_type_general')
        cls.quality_type_2 = cls.env['quality.type'].with_context(tracking_disable=True).create({
            'name': 'General Test',
            'type': 'general',
        })
        cls.quality_point_pass_fail = cls.env['quality.point'].with_context(tracking_disable=True).create({
            'team_id': cls.team.id,
            'type_id': cls.quality_type.id,
        })
        cls.quality_point_measure = cls.env['quality.point'].with_context(tracking_disable=True).create({
            'test_type_id': cls.measure_type.id,
            'team_id': cls.team.id,
            'type_id': cls.quality_type.id,
            'norm': 10.0,
            'tolerance_min': 8.0,
            'tolerance_max': 12.0,
        })
        cls.quality_manager = cls.env.ref('base.user_admin')
        cls.quality_manager.write({
            'groups_id': [(6, 0, [cls.env.ref('to_quality.group_quality_manager').id])]
        })
        cls.quality_user = cls.env.ref('base.user_demo')
        cls.quality_user.write({
            'groups_id': [(6, 0, [cls.env.ref('to_quality.group_quality_user').id])]
        })
        cls.internal_user = cls.env['res.users'].with_context({'no_reset_password': True}).create({
            'name': 'Internal User',
            'login': 'internal',
            'email': 'internal@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])]
        })
