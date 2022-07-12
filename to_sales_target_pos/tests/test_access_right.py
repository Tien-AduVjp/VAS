from datetime import datetime

from odoo.exceptions import AccessError
from odoo.tests import tagged

from odoo.addons.to_sales_target_sale.tests.common import TestTargetSaleCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(TestTargetSaleCommon):

    def test_access_right_pos_user(self):
        self.user_salesman.groups_id = [(6, 0, [self.env.ref('point_of_sale.group_pos_user').id, self.env.ref('base.group_user').id])]
        
        """ Test sale target team/personal of user """
        with self.assertRaises(AccessError):
            self.env['team.sales.target'].with_user(self.user_salesman).create({
                'crm_team_id': self.team1.id,
                'start_date': datetime(2021, 10, 16),
                'end_date': datetime(2021, 10, 18),
                'target': 10
            })
            
        team_target_mine = self.form_create_team_target(self.team1,
                                         datetime(2021, 10, 20),
                                         datetime(2021, 10, 22),
                                         target=100)
                 
        team_target_mine = team_target_mine.with_user(self.user_salesman)
        team_target_mine.read()
        self.assertRaises(AccessError, team_target_mine.write, {'end_date': datetime(2021, 10, 20)})
        self.assertRaises(AccessError, team_target_mine.unlink)
        
        personal_target_mine = team_target_mine.personal_target_ids.filtered(lambda r: r.sale_person_id == self.user_salesman)
        personal_target_mine = personal_target_mine.with_user(self.user_salesman)
        personal_target_mine.read()
        personal_target_mine.write({'target': 10000})
        self.assertRaises(AccessError, personal_target_mine.unlink)
        with self.assertRaises(AccessError), self.cr.savepoint():
            personal_target_mine.sudo().unlink()
            personal_target_mine.create({
                    'sale_person_id': self.user_salesman.id,
                    'team_target_id': team_target_mine.id,
                    'start_date': datetime(2021, 10, 20),
                    'end_date': datetime(2021, 10, 22),
                    'target': 10
                })

        """Test sale target team/personal not belongs user"""
        with self.assertRaises(AccessError):
            self.env['team.sales.target'].with_user(self.user_salesman).create({
                'crm_team_id': self.team2.id,
                'start_date': datetime(2021, 10, 16),
                'end_date': datetime(2021, 10, 18),
                'target': 10
            })
            
        team_target_other_team = self.form_create_team_target(self.team2,
                                 datetime(2021, 10, 20),
                                 datetime(2021, 10, 22),
                                 target=100)
        
        team_target_other_team = team_target_other_team.with_user(self.user_salesman)
        self.assertRaises(AccessError, team_target_other_team.read)
        self.assertRaises(AccessError, team_target_other_team.write, {'end_date': datetime(2021, 10, 20)})
        self.assertRaises(AccessError, team_target_other_team.unlink)

        personal_target_others = (team_target_mine.sudo().personal_target_ids - personal_target_mine)[-1:]
        personal_target_others = personal_target_others.with_user(self.user_salesman)
        self.assertRaises(AccessError, personal_target_others.read)
        self.assertRaises(AccessError, personal_target_others.write, {'target': 10000})
        with self.assertRaises(AccessError), self.cr.savepoint():
            personal_target_others.sudo().unlink()
            personal_target_others.create({
                    'sale_person_id': self.user_salesman.id,
                    'team_target_id': team_target_mine.id,
                    'start_date': datetime(2021, 10, 20),
                    'end_date': datetime(2021, 10, 22),
                    'target': 10
                })
        self.assertRaises(AccessError, personal_target_others.unlink)
        
    def test_access_right_pos_manager(self):
        self.user_salesman.groups_id = [(6, 0, [self.env.ref('point_of_sale.group_pos_manager').id, self.env.ref('base.group_user').id])]
        
        """ Test sale target team/personal of user's team"""
        team_target = self.form_create_team_target(self.team1,
                                         datetime(2021, 10, 16),
                                         datetime(2021, 10, 18),
                                         target=100,
                                         user_create=self.user_leader)
        
        personal_target = team_target.personal_target_ids[-1:]

        personal_target = personal_target.with_user(self.user_leader)
        personal_target.read()
        personal_target.write({'end_date': datetime(2021, 10, 19)})
        personal_target.unlink()
        personal_target.create({
            'sale_person_id': self.user_leader.id,
            'team_target_id': team_target.id,
            'start_date': datetime(2021, 10, 16),
            'end_date': datetime(2021, 10, 18),
            'target': 10
        })

        team_target = team_target.with_user(self.user_leader)
        team_target.read()
        team_target.write({'end_date': datetime(2021, 10, 20)})
        
        """ Test sale personal of other team but belongs sale target user team"""
        personal_target = personal_target.create({
            'sale_person_id': self.user_alldoc.id,
            'team_target_id': team_target.id,
            'start_date': datetime(2021, 10, 16),
            'end_date': datetime(2021, 10, 18),
            'target': 10
        })
        personal_target = personal_target.with_user(self.user_leader)
        personal_target.read()
        personal_target.write({'target': 300})
        personal_target.unlink()
        team_target.unlink()

        """ Test sale target team/personal of other team """
        with self.assertRaises(AccessError):
            self.form_create_team_target(self.team2,
                                         datetime(2021, 10, 16),
                                         datetime(2021, 10, 18),
                                         target=100,
                                         user_create=self.user_leader)
            
        team_target_other_team = self.form_create_team_target(self.team2,
                                         datetime(2021, 10, 21),
                                         datetime(2021, 10, 25),
                                         target=100)
        
        team_target_other_team = team_target_other_team.with_user(self.user_leader)
        self.assertRaises(AccessError, team_target_other_team.read)
        self.assertRaises(AccessError, team_target_other_team.write, {'target': 10000})
        self.assertRaises(AccessError, team_target_other_team.unlink)
        
        personal_target_other_team = team_target_other_team.sudo().personal_target_ids[-1:].with_user(self.user_leader)
        self.assertRaises(AccessError, personal_target_other_team.read)
        self.assertRaises(AccessError, personal_target_other_team.write, {'target': 10000})
        self.assertRaises(AccessError, personal_target_other_team.unlink)
        with self.assertRaises(AccessError):
            personal_target_other_team.create({
                'sale_person_id': self.user_leader.id,
                'team_target_id': team_target_other_team.id,
                'start_date': datetime(2021, 10, 21),
                'end_date': datetime(2021, 10, 25),
                'target': 10
            })

        # Force change user team 2 to team 1 (Have permission with personal target but not with team target) => Only can read
        person_change_team = personal_target_other_team.sudo().sale_person_id
        self.team1.member_ids = ([4, person_change_team.id])
        personal_target_other_team.read()
        self.assertRaises(AccessError, personal_target_other_team.write, {'target': 10000})
        self.assertRaises(AccessError, personal_target_other_team.unlink)
        team_target_other_team.sudo().personal_target_ids.unlink()
        with self.assertRaises(AccessError):
            personal_target_other_team.create({
                'sale_person_id': person_change_team.id,
                'team_target_id': team_target_other_team.id,
                'start_date': datetime(2021, 10, 21),
                'end_date': datetime(2021, 10, 25),
                'target': 10
            })
        self.assertRaises(AccessError, team_target_other_team.read)
        self.assertRaises(AccessError, team_target_other_team.write, {'target': 10000})
        self.assertRaises(AccessError, team_target_other_team.unlink)
