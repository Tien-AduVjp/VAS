import psycopg2
from odoo.tools import mute_logger
from odoo.tests.common import tagged, users
from .common import Common


@tagged('-at_install', 'post_install')
class Quality(Common):

    def test_31_action_name_unique(self):
        """
        Case 4: Check for duplication of quality actions
        """
        self.quality_action = self.env['quality.action'].with_context(tracking_disable=True).create({
            'name': 'Action 1',
        })
        with self.assertRaises(psycopg2.IntegrityError), mute_logger('odoo.sql_db'):
            self.quality_action = self.env['quality.action'].with_context(tracking_disable=True).create({
                'name': 'Action 1',
            })

    @users('demo', 'internal')
    def test_pass_fail_check_flow(self):
        """ Test the workflow of check with pass/fail type """
        quality_check_1 = self.env['quality.check'].sudo().with_context(tracking_disable=True).create({
            'type_id': self.quality_type.id,
            'point_id': self.quality_point_pass_fail.id,
            'team_id': self.quality_point_pass_fail.team_id.id,
            'user_id': self.env.user.id,
        })
        quality_check_1.do_pass()
        self.assertEqual(quality_check_1.quality_state, 'pass')

        quality_check_2 = self.env['quality.check'].sudo().with_context(tracking_disable=True).create({
            'type_id': self.quality_type.id,
            'point_id': self.quality_point_pass_fail.id,
            'team_id': self.quality_point_pass_fail.team_id.id,
            'user_id': self.env.user.id,
        })
        quality_check_2.do_fail()
        self.assertEqual(quality_check_2.quality_state, 'fail')

    @users('demo', 'internal')
    def test_measure_check_flow(self):
        """ Test the workflow of check with measure type """
        quality_check_1 = self.env['quality.check'].sudo().with_context(tracking_disable=True).create({
            'type_id': self.quality_type.id,
            'point_id': self.quality_point_measure.id,
            'team_id': self.quality_point_measure.team_id.id,
            'user_id': self.env.user.id,
        })
        quality_check_1.measure = 5  # out normal range
        res = quality_check_1.do_measure()
        # Warning popup should appear
        self.assertEqual(res['type'], 'ir.actions.act_window')
        self.assertEqual(res['view_id'], self.env.ref('to_quality.quality_check_view_form_failure').id)
        self.assertEqual(quality_check_1.quality_state, 'none')

        quality_check_2 = self.env['quality.check'].sudo().with_context(tracking_disable=True).create({
            'type_id': self.quality_type.id,
            'point_id': self.quality_point_measure.id,
            'team_id': self.quality_point_measure.team_id.id,
            'user_id': self.env.user.id,
        })
        quality_check_2.measure = 11  # in normal range
        res = quality_check_2.do_measure()
        # Warning popup won't appear
        self.assertEqual(res, None)
        self.assertEqual(quality_check_2.quality_state, 'pass')
