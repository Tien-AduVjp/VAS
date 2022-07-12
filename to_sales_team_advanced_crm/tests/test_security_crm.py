from odoo.exceptions import AccessError
from odoo.tests import tagged

from odoo.addons.to_sales_team_advanced.tests.test_default_team import TestDefaultTeamCommon


@tagged('post_install', '-at_install')
class TestSalesTeamAdvancedSaleSecurity(TestDefaultTeamCommon):

    @classmethod
    def setUpClass(cls):
        super(TestSalesTeamAdvancedSaleSecurity, cls).setUpClass()
        cls.team_1.write({
            'member_ids': [(6, 0, [cls.user_1.id, cls.user_2.id])],
            'crm_team_region_id': cls.sale_rg_1.id
        })
        cls.team_2.write({
            'member_ids': [(6, 0, [cls.user_3.id])],
            'crm_team_region_id': cls.sale_rg_2.id
        })
        cls.team_3.write({
            'member_ids': [(6, 0, [cls.user.id])],
            'crm_team_region_id': cls.sale_rg_1.id
        })
        CRMLead = cls.env['crm.lead']
        cls.lead_1 = CRMLead.create({
            'name': 'lead_1',
            'user_id': cls.user_1.id,
            'team_id': cls.team_1.id,
            'crm_team_region_id': cls.sale_rg_1.id
        })
        cls.pl_1 = CRMLead.create({
            'name': 'pl_1',
            'user_id': cls.user_1.id,
            'team_id': cls.team_1.id,
            'crm_team_region_id': cls.sale_rg_1.id,
            'type': 'opportunity'
        })
        cls.lead_2 = CRMLead.create({
            'name': 'lead_2',
            'user_id': cls.user_2.id,
            'team_id': cls.team_1.id,
            'crm_team_region_id': cls.sale_rg_1.id,
        })
        cls.pl_2 = CRMLead.create({
            'name': 'pl_2',
            'user_id': cls.user_2.id,
            'team_id': cls.team_1.id,
            'crm_team_region_id': cls.sale_rg_1.id,
            'type': 'opportunity'
        })
        cls.lead_3 = CRMLead.create({
            'name': 'lead_3',
            'user_id': cls.user_3.id,
            'team_id': cls.team_2.id,
            'crm_team_region_id': cls.sale_rg_2.id
        })
        cls.pl_3 = CRMLead.create({
            'name': 'pl_3',
            'user_id': cls.user_3.id,
            'team_id': cls.team_2.id,
            'crm_team_region_id': cls.sale_rg_2.id,
            'type': 'opportunity'
        })
        cls.lead_4 = CRMLead.create({
            'name': 'lead_4',
            'user_id': False,
            'team_id': False
        })
        cls.pl_4 = CRMLead.create({
            'name': 'pl_3',
            'type': 'opportunity',
            'user_id': False,
            'team_id': False
        })
        cls.partner = cls.env['res.partner'].create({'name': 'test_crm_partner'})

    def test_2000_group_sale_team_leader_member(self):
        """ user_2 has group_sale_team_leader and is member of team_1
            user_2 can read, write, change state all document of team_1
            user_2 can't read, write, unlink, change state all document of another team """

        group_sale_team_leader = self.env.ref('to_sales_team_advanced.group_sale_team_leader').id
        self.user_2.write({
            'groups_id': [(6, 0, [group_sale_team_leader])],
        })

        self.lead_2.with_user(self.user_2).read(['id'])
        self.lead_2.with_user(self.user_2).write({'name': 'test'})
        self.lead_2.with_user(self.user_2).convert_opportunity(self.partner.id)

        self.assertRaises(AccessError, self.lead_2.with_user(self.user_2).unlink)
        self.pl_2.with_user(self.user_2).read(['id'])
        self.pl_2.with_user(self.user_2).write({'name': 'test'})
        self.pl_2.with_user(self.user_2).action_set_won_rainbowman()
        self.assertRaises(AccessError, self.pl_2.with_user(self.user_2).unlink)

        self.lead_1.with_user(self.user_2).read(['id'])
        self.lead_1.with_user(self.user_2).write({'name': 'test'})
        self.lead_1.with_user(self.user_2).convert_opportunity(self.partner.id)
        self.assertRaises(AccessError, self.lead_1.with_user(self.user_2).unlink)

        self.pl_1.with_user(self.user_2).read(['id'])
        self.pl_1.with_user(self.user_2).write({'name': 'test'})
        self.pl_1.with_user(self.user_2).action_set_won_rainbowman()
        self.assertRaises(AccessError, self.pl_1.with_user(self.user_2).unlink)

        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).read, ['id'])
        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).write, {'name': 'test'})
        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).convert_opportunity, self.partner.id)
        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).unlink)

        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).read, ['id'])
        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).write, {'name': 'test'})
        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).action_set_won_rainbowman)
        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).unlink)

        self.lead_4.with_user(self.user_2).read(['id'])
        self.lead_4.with_user(self.user_2).write({'name': 'test'})
        self.lead_4.with_user(self.user_2).convert_opportunity(self.partner.id)
        self.assertRaises(AccessError, self.lead_4.with_user(self.user_2).unlink)

        self.pl_4.with_user(self.user_2).read(['id'])
        self.pl_4.with_user(self.user_2).write({'name': 'test'})
        self.pl_4.with_user(self.user_2).action_set_won_rainbowman()
        self.assertRaises(AccessError, self.pl_4.with_user(self.user_2).unlink)

    def test_2001_group_sale_team_leader_leader(self):
        """ user_2 has group_sale_team_leader and is team leader of team_1
            user_2 can read, write, change state all document of team_1
            user_2 can't read, write, unlink, change state all document of another team """
        self.sale_rg_1.write({
            'user_id': self.user_2.id
        })
        self.team_1.write({
            'user_id': self.user_2.id,
            'member_ids': [(3, self.user_2.id)]
        })
        self.test_2000_group_sale_team_leader_member()

    def test_2002_group_sale_regional_manager_member(self):
        """ user_2 has group_sale_regional_manager
            user_2 can read, write, change state all document of sale_rg_1
            user_2 can't read, write, unlink, change state all document of another sale regional """

        group_sale_regional_manager = self.env.ref('to_sales_team_advanced.group_sale_regional_manager').id
        self.user_2.write({
            'groups_id': [(6, 0, [group_sale_regional_manager])],
        })

        self.pl_2.with_user(self.user_2).read(['id'])
        self.pl_2.with_user(self.user_2).write({'name': 'test'})
        self.pl_2.with_user(self.user_2).action_set_won_rainbowman()
        self.assertRaises(AccessError, self.pl_2.with_user(self.user_2).unlink)

        self.lead_1.with_user(self.user_2).read(['id'])
        self.lead_1.with_user(self.user_2).write({'name': 'test'})
        self.lead_1.with_user(self.user_2).convert_opportunity(self.partner.id)
        self.assertRaises(AccessError, self.lead_1.with_user(self.user_2).unlink)

        self.pl_1.with_user(self.user_2).read(['id'])
        self.pl_1.with_user(self.user_2).write({'name': 'test'})
        self.pl_1.with_user(self.user_2).action_set_won_rainbowman()
        self.assertRaises(AccessError, self.pl_1.with_user(self.user_2).unlink)

        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).read, ['id'])
        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).write, {'name': 'test'})
        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).convert_opportunity, self.partner.id)
        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).unlink)

        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).read, ['id'])
        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).write, {'name': 'test'})
        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).action_set_won_rainbowman)
        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).unlink)

        self.lead_4.with_user(self.user_2).read(['id'])
        self.lead_4.with_user(self.user_2).write({'name': 'test'})
        self.lead_4.with_user(self.user_2).convert_opportunity(self.partner.id)
        self.assertRaises(AccessError, self.lead_4.with_user(self.user_2).unlink)

        self.pl_4.with_user(self.user_2).read(['id'])
        self.pl_4.with_user(self.user_2).write({'name': 'test'})
        self.pl_4.with_user(self.user_2).action_set_won_rainbowman()
        self.assertRaises(AccessError, self.pl_4.with_user(self.user_2).unlink)

    def test_2003_group_sale_regional_manager_direct(self):
        """ user has group group_sale_regional_manager and is region manager of team_2's region
            user_2 can read, write, change state, mark won of all team's document """

        self.team_1.member_ids = [(3, self.user_2.id)]
        self.sale_rg_1.user_id = self.user_2

        self.test_2002_group_sale_regional_manager_member()

    def test_2004_group_sale_regional_manager_parent(self):
        """ user has group group_sale_regional_manager and is region manager of team_2's region parent
            user_2 can read, write, change state, mark won of all team's document """

        self.team_1.member_ids = [(3, self.user_2.id)]
        self.sale_rg_3.user_id = self.user_2
        self.sale_rg_1.parent_id = self.sale_rg_3

        self.test_2002_group_sale_regional_manager_member()
    
    def test_2005_group_sale_regional_manager_child(self):
        """ user has group group_sale_regional_manager and is region manager of team_2's region child
            user_2 don't have permission to read, write, change state, mark won of all team's document """
        
        self.user_2.groups_id = [(6, 0, self.env.ref('to_sales_team_advanced.group_sale_regional_manager').ids)]
        
        self.team_1.write({
            'member_ids': [(3, self.user_2.id)],
            'crm_team_region_id': self.sale_rg_1.id
            })
        
        self.sale_rg_3.write({
            'user_id': self.user_2.id,
            'parent_id': self.sale_rg_1.id
            })
        
        self.assertRaises(AccessError, self.lead_1.with_user(self.user_2).read, ['id'])
        self.assertRaises(AccessError, self.lead_1.with_user(self.user_2).write, {'name': 'test'})
        self.assertRaises(AccessError, self.lead_1.with_user(self.user_2).convert_opportunity, self.partner.id)
        self.assertRaises(AccessError, self.lead_1.with_user(self.user_2).unlink)

        self.assertRaises(AccessError, self.pl_1.with_user(self.user_2).read, ['id'])
        self.assertRaises(AccessError, self.pl_1.with_user(self.user_2).write, {'name': 'test'})
        self.assertRaises(AccessError, self.pl_1.with_user(self.user_2).action_set_won_rainbowman)
        self.assertRaises(AccessError, self.pl_1.with_user(self.user_2).unlink)

        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).read, ['id'])
        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).write, {'name': 'test'})
        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).convert_opportunity, self.partner.id)
        self.assertRaises(AccessError, self.lead_3.with_user(self.user_2).unlink)

        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).read, ['id'])
        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).write, {'name': 'test'})
        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).action_set_won_rainbowman)
        self.assertRaises(AccessError, self.pl_3.with_user(self.user_2).unlink)

        self.lead_4.with_user(self.user_2).read(['id'])
        self.lead_4.with_user(self.user_2).write({'name': 'test'})
        self.lead_4.with_user(self.user_2).convert_opportunity(self.partner.id)
        self.assertRaises(AccessError, self.lead_4.with_user(self.user_2).unlink)

        self.pl_4.with_user(self.user_2).read(['id'])
        self.pl_4.with_user(self.user_2).write({'name': 'test'})
        self.pl_4.with_user(self.user_2).action_set_won_rainbowman()
        self.assertRaises(AccessError, self.pl_4.with_user(self.user_2).unlink)
