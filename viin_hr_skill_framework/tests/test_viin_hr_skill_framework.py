from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools.misc import mute_logger
from odoo.exceptions import UserError

from .common import Common

@tagged('post_install', '-at_install')
class TestViinHrRank(Common):

    def test_hr_rank_skill_description_sql_constraints(self):
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['hr.rank.skill.description'].with_context(tracking_disable=True).create({
                'rank_id' : self.rank_common.id,
                'skill_type_id' : self.skill_type_1.id,
                'skill_id': self.skill_2.id,
                'skill_level_id': self.level_intermediate.id             
                })

    def test_hr_skill_description_sql_constraints(self):
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['hr.skill.description'].with_context(tracking_disable=True).create({
                'skill_type_id' : self.skill_type_1.id,
                'skill_id': self.skill_2.id,
                'skill_level_id': self.level_intermediate.id         
                })
            
    def test_hr_rank_skill_description_api_contraints_1(self):
        with self.assertRaises(UserError):
            self.rank_skill_description_test = self.env['hr.rank.skill.description'].with_context(tracking_disable=True).create({
                'rank_id' : self.rank_common.id,
                'skill_type_id' : self.skill_type_1.id,
                'skill_id': self.skill_2.id,
                'skill_level_id': self.level_beginner.id,
                'expectation' : 'preferred'
                })

    def test_hr_rank_skill_description_api_contraints_2(self):
        with self.assertRaises(UserError):
            self.rank_skill_description.write({
                'expectation' : 'preferred'
                })
            self.rank_skill_description_test = self.env['hr.rank.skill.description'].with_context(tracking_disable=True).create({
                'rank_id' : self.rank_common.id,
                'skill_type_id' : self.skill_type_1.id,
                'skill_id': self.skill_2.id,
                'skill_level_id': self.level_expert.id,
                'expectation' : 'required'
                })
