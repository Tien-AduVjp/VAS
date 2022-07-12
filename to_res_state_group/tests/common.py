from odoo.tests.common import SavepointCase


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        #Group
        group_partner_manager = cls.env.ref('base.group_partner_manager')

        #User
        cls.user_partner_manager = cls.env.ref('base.user_demo')
        cls.user_partner_manager.write({'groups_id': [(4, group_partner_manager.id, 0)]})

        #Country
        cls.country1 = cls.env.ref('base.vn')
        cls.country2 = cls.env.ref('base.jp')

        #Country State
        cls.country_state1 = cls.env.ref('base.state_vn_VN-HP')
        cls.country_state2 = cls.env.ref('base.state_jp_jp-34')
        cls.country_state3 = cls.env.ref('base.state_vn_VN-HN')

        #State Group
        cls.state_group1 = cls.env['res.state.group'].create({
            'name': 'State Group 1',
            'code': 'SG1',
            'country_id': cls.country1.id,
            'state_ids': [cls.country_state3.id]
        })
        cls.state_group2 = cls.env['res.state.group'].create({
            'name': 'State Group 2',
            'code': 'SG2',
            'country_id': cls.country2.id,
            'state_ids': [cls.country_state2.id]
        })
