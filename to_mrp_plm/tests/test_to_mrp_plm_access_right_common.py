from odoo.tests.common import SavepointCase


class TestAccessRightCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccessRightCommon, cls).setUpClass()
        ResUsers = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.mrp_user = ResUsers.create({
            'name': 'MRP User',
            'login': 'mrp_user',
            'email': 'mrp_user@example.com',
            'groups_id': [(6, 0, [cls.env.ref('mrp.group_mrp_user').id])]
        })

        cls.plm_user = ResUsers.create({
            'name': 'PLM User ',
            'login': 'plm_user',
            'email': 'plm_user@example.com',
            'groups_id': [(6, 0, [cls.env.ref('to_mrp_plm.group_plm_user').id])]
        })

        cls.plm_manager = ResUsers.create({
            'name': 'PLM Manager',
            'login': 'plm_manager',
            'email': 'plm_manager@example.com',
            'groups_id': [(6, 0, [cls.env.ref('to_mrp_plm.group_plm_manager').id])]
        })

        cls.type = cls.env.ref('to_mrp_plm.eco_type0')
        cls.bom = cls.env.ref('mrp.mrp_bom_desk')
        cls.product = cls.env.ref('mrp.product_product_wood_panel')
        cls.stage = cls.env.ref('to_mrp_plm.eco_stage_new')
        cls.eco = cls.env['mrp.eco']

        cls.eco1 = cls.eco.create({
            'name': 'Change Funiture BoM',
            'stage_id': cls.stage.id,
            'type_id': cls.type.id,
            'type': 'bom',
            'product_tmpl_id': cls.bom.product_tmpl_id.id,
            'bom_id':cls.bom.id
            })

        cls.template = cls.env['mrp.eco.approval.template'].create({
            'name': 'Expert comments',
            'user_ids': [(4, cls.mrp_user.id)],
            'approval_type': 'comment',
            'stage_id': cls.stage.id
            })

        cls.approval = cls.env['mrp.eco.approval'].create({
            'name': 'Commnent',
            'eco_id': cls.eco1.id,
            'approval_template_id': cls.template.id
            })

        cls.tag = cls.env['mrp.eco.tag'].create({'name': 'Change'})
