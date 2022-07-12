from odoo.addons.to_quality.tests.common import Common as QualityCommon


class Common(QualityCommon):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.product_tmpl_a = cls.env.ref('product.product_product_11_product_template')
        cls.product_a1 = cls.product_tmpl_a.product_variant_ids[0]
        cls.product_a2 = cls.product_tmpl_a.product_variant_ids[1]
        cls.product_tmpl_b = cls.env.ref('product.product_product_4_product_template')
        cls.product_c = cls.env.ref('product.product_product_3')
        cls.quality_point_pass_fail_2 = cls.env['quality.point'].with_context(tracking_disable=True).create({
            'type_id': cls.quality_type.id,
            'team_id': cls.team.id,
            'product_tmpl_id': cls.product_tmpl_a.id
        })
        cls.quality_point_measure_2 = cls.env['quality.point'].with_context(tracking_disable=True).create({
            'type_id': cls.quality_type.id,
            'test_type_id': cls.measure_type.id,
            'team_id': cls.team.id,
            'product_tmpl_id': cls.product_tmpl_a.id
        })
