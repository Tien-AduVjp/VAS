from odoo.tests.common import SavepointCase


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.product_tmpl_a = cls.env.ref('product.product_product_11_product_template')
        cls.product_a1 = cls.product_tmpl_a.product_variant_ids[0]
        cls.product_a2 = cls.product_tmpl_a.product_variant_ids[1]
        cls.product_tmpl_b = cls.env.ref('product.product_product_4_product_template')

        cls.product_c = cls.env.ref('product.product_product_3')
        cls.measure_type = cls.env.ref('to_quality.test_type_measure')
        cls.team = cls.env.ref('to_quality.quality_alert_team0')
        cls.quality_point_pass_fail = cls.env['quality.point'].with_context(tracking_disable=True).create({
            'product_tmpl_id': cls.product_tmpl_a.id,
            'team_id': cls.team.id,
        })
        cls.quality_point_measure = cls.env['quality.point'].with_context(tracking_disable=True).create({
            'product_tmpl_id': cls.product_tmpl_a.id,
            'test_type_id': cls.measure_type.id,
            'team_id': cls.team.id,
        })
        cls.quality_manager = cls.env.ref('base.user_admin')
        cls.quality_manager.write({
            'groups_id': [(6, 0, [cls.env.ref('to_quality.group_quality_manager').id])]
        })
        cls.quality_user = cls.env.ref('base.user_demo')
        cls.quality_user.write({
            'groups_id': [(6, 0, [cls.env.ref('to_quality.group_quality_user').id])]
        })
