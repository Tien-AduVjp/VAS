from datetime import datetime

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from .target_common import TargetCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(TargetCommon):

    @classmethod
    def setUpClass(cls):
        super(TestAccessRight, cls).setUpClass()

        # Create data Sale team's target and Sale personal target
        cls.SalesTarget = cls.env['team.sales.target']
        cls.team1_target = cls.form_create_team_target(cls.team1,
                                                       datetime(2021, 8, 16),
                                                       datetime(2021, 8, 18),
                                                       target=1000)

        cls.team2_target = cls.form_create_team_target(cls.team2,
                                                       datetime(2021, 8, 26),
                                                       datetime(2021, 8, 28))

    def test_access_right_01_sale_user(self):
        team1_target_mine = self.team1_target.with_user(self.user_salesman)
        team2_target_other_team = self.team2_target.with_user(self.user_salesman)
        user_target_mine = self.team1_target.personal_target_ids \
                                    .filtered(lambda r: r.sale_person_id == self.user_salesman).with_user(self.user_salesman)
        user_target_others = self.team2_target.personal_target_ids[0].with_user(self.user_salesman)
        # The only thing a sales user can do is read their sale team's target, their sale target and change target in their sale target
        # Test with their sale team's target
        team1_target_mine.read()
        self.assertRaises(AccessError, team1_target_mine.write, {'target': 100})
        self.assertRaises(AccessError, team1_target_mine.unlink)
        with self.assertRaises(AccessError), self.cr.savepoint():
            team1_target_mine.create({
                'crm_team_id': self.team1.id,
                'start_date': datetime(2022, 8, 16),
                'end_date': datetime(2022, 8, 18),
                'target': 10
            })
        # Test with sale target of another team
        self.assertRaises(AccessError, team2_target_other_team.read)
        self.assertRaises(AccessError, team2_target_other_team.write, {'target': 100})
        self.assertRaises(AccessError, team2_target_other_team.unlink)

        # Test with their target
        user_target_mine.read()
        user_target_mine.target = 10000
        self.assertRaises(AccessError, user_target_mine.unlink)
        with self.assertRaises(AccessError):
            user_target_mine.sudo().unlink()
            user_target_mine.create({
                'sale_person_id': self.user_salesman.id,
                'team_target_id': team1_target_mine.id,
                'start_date': datetime(2022, 8, 16),
                'end_date': datetime(2022, 8, 18),
                'target': 10
            })

        # Test with other personal target
        self.assertRaises(AccessError, user_target_others.read)
        self.assertRaises(AccessError, user_target_others.write, {'target': 300})
        self.assertRaises(AccessError, user_target_others.unlink)

    def test_access_right_02_sale_leader(self):
        team1_target_lead = self.team1_target.with_user(self.user_leader)
        team2_target_other_team = self.team2_target.with_user(self.user_leader)
        user_target_lead = self.team1_target.personal_target_ids[0].with_user(self.user_leader)
        user_target_other_team = self.team2_target.personal_target_ids[0].with_user(self.user_leader)
        # A sales team leader may do anything except approve their sales team's and salesperson's objective for their team.
        # Test with their sale team's target
        team1_target_lead.read()
        team1_target_lead.write({'start_date': datetime(2021, 8, 15)})
        with self.assertRaises(UserError), self.cr.savepoint():
            team1_target_lead.unlink()
            team1_target_lead.create({
                'crm_team_id': self.team1.id,
                'start_date': datetime(2022, 8, 16),
                'end_date': datetime(2022, 8, 18),
                'target': 10
            })
            raise UserError('trick to rollback')
        # Test with sale target of another team
        self.assertRaises(AccessError, team2_target_other_team.read)
        self.assertRaises(AccessError, team2_target_other_team.write, {'target': 100})
        self.assertRaises(AccessError, team2_target_other_team.unlink)
        with self.assertRaises(AccessError), self.cr.savepoint():
            team2_target_other_team.create({
                'crm_team_id': self.team2.id,
                'start_date': datetime(2022, 8, 16),
                'end_date': datetime(2022, 8, 18),
                'target': 10
            })

        # Test with sale personal target of their team
        user_target_lead.read()
        user_target_lead.write({'start_date': datetime(2021, 8, 16), 'target': 10000})
        sale_person = user_target_lead.sale_person_id
        user_target_lead.unlink()
        user_target_lead.create({
            'sale_person_id': sale_person.id,
            'team_target_id': team1_target_lead.id,
            'start_date': datetime(2021, 8, 16),
            'end_date': datetime(2021, 8, 18),
            'target': 1000
        })
        
        # Sales person belongs team 1 of User belongs team2
        person_target_except = self.env['personal.sales.target'].with_user(self.user_leader).create({
                'team_target_id': self.team1_target.id,
                'sale_person_id': self.user_alldoc.id,
                'start_date': datetime(2021, 8, 16),
                'end_date': datetime(2021, 8, 18),
                'target': 100
            })
        person_target_except.read()
        person_target_except.write({'target': 200})
        person_target_except.unlink()
        
        # Test with sale personal target of other team
        self.assertRaises(AccessError, user_target_other_team.read)
        self.assertRaises(AccessError, user_target_other_team.write, {'target': 300})
        self.assertRaises(AccessError, user_target_other_team.unlink)
        with self.assertRaises(AccessError):
            user_target_other_team.create({
            'sale_person_id': sale_person.id,
            'team_target_id': team2_target_other_team.id,
            'start_date': datetime(2022, 8, 16),
            'end_date': datetime(2022, 8, 18),
            'target': 1000
        })

    def test_access_right_03_regional_manager(self):
        team1_target_region = self.team1_target.with_user(self.user_regional)
        team2_target_region = self.team2_target.with_user(self.user_regional)
        user_target1_region = self.team1_target.personal_target_ids[0].with_user(self.user_regional)
        user_target2_region = self.team2_target.personal_target_ids[0].with_user(self.user_regional)

        # A sales team regional manager may do anything to their sales team's and salesperson's objective which is managed by them
        # Test with their sale team's target
        team1_target_region.read()
        team2_target_region.read()
        team1_target_region.write({'start_date': datetime(2021, 8, 15), 'target': 10000})
        team2_target_region.write({'start_date': datetime(2021, 8, 25), 'target': 10000})
        with self.assertRaises(UserError), self.cr.savepoint():
            team1_target_region.unlink()
            team1_target_region.create({
                'crm_team_id': self.team1.id,
                'start_date': datetime(2022, 8, 16),
                'end_date': datetime(2022, 8, 18),
                'target': 10
            })
            team2_target_region.unlink()
            team2_target_region.create({
                'crm_team_id': self.team2.id,
                'start_date': datetime(2022, 8, 16),
                'end_date': datetime(2022, 8, 18),
                'target': 10
            })
            raise UserError('trick to rollback')

        # Test with sale personal target of their team
        user_target1_region.read()
        user_target2_region.read()
        user_target1_region.write({'start_date': datetime(2021, 8, 16), 'target': 10000})
        user_target2_region.write({'start_date': datetime(2021, 8, 26), 'target': 10000})

        sale_person = user_target1_region.sale_person_id
        user_target1_region.unlink()
        user_target1_region.create({
            'sale_person_id': sale_person.id,
            'team_target_id': team1_target_region.id,
            'start_date': datetime(2021, 8, 16),
            'end_date': datetime(2021, 8, 18),
            'target': 1000
        })

        sale_person = user_target2_region.sale_person_id
        user_target2_region.unlink()
        user_target2_region = user_target2_region.create({
            'sale_person_id': sale_person.id,
            'team_target_id': team2_target_region.id,
            'start_date': datetime(2021, 8, 26),
            'end_date': datetime(2021, 8, 28),
            'target': 1000
        })
        
        # Person target of User team 2 that belongs target team 1
        person_target_except = self.env['personal.sales.target'].with_user(self.user_leader).create({
                'team_target_id': self.team1_target.id,
                'sale_person_id': self.user_alldoc.id,
                'start_date': datetime(2021, 8, 16),
                'end_date': datetime(2021, 8, 18),
                'target': 100
            })
        person_target_except.read()
        person_target_except.write({'target': 200})
        with self.assertRaises(UserError), self.cr.savepoint():
            person_target_except.unlink()
            raise UserError('trick to rollback')

        # Test with team sale target of another team
        self.team2.crm_team_region_id = self.region2
        self.assertRaises(AccessError, team2_target_region.read)
        self.assertRaises(AccessError, team2_target_region.write, {'target': 100})
        self.assertRaises(AccessError, team2_target_region.unlink)
        with self.assertRaises(AccessError):
            team2_target_region.create({
                'crm_team_id': self.team2.id,
                'start_date': datetime(2022, 7, 16),
                'end_date': datetime(2022, 7, 18),
                'target': 10
            })

        # Test with sale personal target of other team
        self.assertRaises(AccessError, user_target2_region.read)
        self.assertRaises(AccessError, user_target2_region.write, {'target': 300})
        self.assertRaises(AccessError, user_target2_region.unlink)
        with self.assertRaises(AccessError):
            user_target2_region.sudo().unlink()
            user_target2_region.create({
                'sale_person_id': sale_person.id,
                'team_target_id': team2_target_region.id,
                'start_date': datetime(2021, 7, 16),
                'end_date': datetime(2021, 7, 19),
                'target': 1000
            })

        person_target_except.read()
        person_target_except.write({'target': 200})
        person_target_except.unlink()

    def test_access_right_04_all_document(self):
        team1_target = self.team1_target.with_user(self.user_alldoc)
        team2_target = self.team2_target.with_user(self.user_alldoc)  # The regions of team 1 and team 2 are distinct.
        user_target1 = self.team1_target.personal_target_ids[0].with_user(self.user_alldoc)
        user_target2 = self.team2_target.personal_target_ids[0].with_user(self.user_alldoc)

        # A all document user and admin user have unrestricted right so they can do anything.
        # Test with sale team's target
        team1_target.read()
        team2_target.read()
        team1_target.write({'start_date': datetime(2021, 8, 15), 'target': 10000})
        team2_target.write({'start_date': datetime(2021, 8, 25), 'target': 10000})
        with self.assertRaises(UserError), self.cr.savepoint():
            team1_target.unlink()
            team1_target.create({
                'crm_team_id': self.team1.id,
                'start_date': datetime(2022, 8, 16),
                'end_date': datetime(2022, 8, 18),
                'target': 10
            })
            team2_target.unlink()
            team2_target.create({
                'crm_team_id': self.team2.id,
                'start_date': datetime(2022, 8, 16),
                'end_date': datetime(2022, 8, 18),
                'target': 10
            })
            raise UserError('trick to rollback')

        # Test with sale personal target
        user_target1.read()
        user_target2.read()
        user_target1.write({'start_date': datetime(2021, 8, 16), 'target': 10000})
        user_target2.write({'start_date': datetime(2021, 8, 26), 'target': 10000})

        sale_person = user_target1.sale_person_id
        user_target1.unlink()
        user_target1.create({
            'sale_person_id': sale_person.id,
            'team_target_id': team1_target.id,
            'start_date': datetime(2021, 8, 16),
            'end_date': datetime(2021, 8, 18),
            'target': 1000
        })

        sale_person = user_target2.sale_person_id
        user_target2.unlink()
        user_target2 = user_target2.create({
            'sale_person_id': sale_person.id,
            'team_target_id': team2_target.id,
            'start_date': datetime(2021, 8, 26),
            'end_date': datetime(2021, 8, 28),
            'target': 1000
        })
