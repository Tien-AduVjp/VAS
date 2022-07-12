from datetime import datetime
from odoo.tests.common import tagged
from odoo.exceptions import AccessError
from .common import Common


@tagged('-at_install', 'post_install', 'access_rights')
class QualityAccessRight(Common):

    def setUp(self):
        super(QualityAccessRight, self).setUp()
        self.quality_alert_stage = self.env.ref('to_quality.quality_alert_stage_0')
        self.quality_measure = self.env.ref('to_quality.test_type_measure')

        self.quality_tag = self.env['quality.tag'].create({
            'name': 'Quality Tag',
        })
        self.quality_reason = self.env['quality.reason'].create({
            'name': 'Quality Reason',
        })

    def test_01_quality_user(self):
        # Quality User can create the quality check
        quality_check = self.env['quality.check'].with_context(tracking_disable=True).with_user(self.quality_user).create({
            'product_id': self.quality_point_measure.product_id.id,
            'team_id': self.quality_point_measure.team_id.id,
            'checked_quantity': 80.00
        })
        # Quality User can see the quality check
        quality_check.with_user(self.quality_user).read()
        # Quality User can edit the quality check
        quality_check.with_user(self.quality_user).write({
            'checked_quantity': 90.00
        })
        # Quality User can't delete the quality check
        with self.assertRaises(AccessError):
            quality_check.with_user(self.quality_user).unlink()

        # Quality User can create the quality alert
        quality_alert = self.env['quality.alert'].with_context(tracking_disable=True).with_user(self.quality_user).create({
            'product_tmpl_id': self.product_tmpl_a.id,
            'team_id': self.quality_point_measure.team_id.id,
            'stage_id': self.quality_alert_stage.id
        })
        # Quality User can see the quality alert
        quality_alert.with_user(self.quality_user).read()
        # Quality User can edit the quality alert
        quality_alert.with_user(self.quality_user).write({
            'name': 'New Alert 1'
        })
        # Quality User can't delete the quality alert
        with self.assertRaises(AccessError):
            quality_alert.with_user(self.quality_user).unlink()

        # Quality User can see the quality point
        self.quality_point_measure.with_user(self.quality_user).read()
        # Quality User can't edit the quality point
        with self.assertRaises(AccessError):
            self.quality_point_measure.with_user(self.quality_user).write({
                'name': 'New Point'
            })
        # Quality User can't create the quality point
        with self.assertRaises(AccessError):
            self.env['quality.point'].with_context(tracking_disable=True).with_user(self.quality_user).create({
                'product_tmpl_id': self.product_tmpl_a.id,
                'test_type_id': self.measure_type.id,
                'team_id': self.team.id,
            })
        # Quality User can't unlink the quality point
        with self.assertRaises(AccessError):
            self.quality_point_measure.with_user(self.quality_user).unlink()

        # Quality User can see the quality team
        self.team.with_user(self.quality_user).read()
        # Quality User can't edit the quality team
        with self.assertRaises(AccessError):
            self.team.with_user(self.quality_user).write({
                'name': 'New Team'
            })
        # Quality User can't create the quality team
        with self.assertRaises(AccessError):
            self.env['quality.alert.team'].with_user(self.quality_user).create({
                'name': 'New Team 1',
                'alias_id': self.env.ref('to_quality.mail_alias_quality_alert').id
            })
        # Quality User can't delete the quality team
        with self.assertRaises(AccessError):
            self.team.with_user(self.quality_user).unlink()

        # Quality User can see the quality tag
        self.quality_tag.with_user(self.quality_user).read()
        # Quality User can't edit the quality tag
        with self.assertRaises(AccessError):
            self.quality_tag.with_user(self.quality_user).write({
                'name': 'New Tag'
            })
        # Quality User can't create the quality tag
        with self.assertRaises(AccessError):
            self.env['quality.tag'].with_user(self.quality_user).create({
                'name': 'New Tag 1',
            })
        # Quality User can't delete the quality tag
        with self.assertRaises(AccessError):
            self.quality_tag.with_user(self.quality_user).unlink()

        # Quality User can see the quality alert stage
        self.quality_alert_stage.with_user(self.quality_user).read()
        # Quality User can't edit the quality alert stage
        with self.assertRaises(AccessError):
            self.quality_alert_stage.with_user(self.quality_user).write({
                'name': 'New Alert Stage'
            })
        # Quality User can't create the quality alert stage
        with self.assertRaises(AccessError):
            self.env['quality.alert.stage'].with_user(self.quality_user).create({
                'name': 'New Alert Stage 1',
            })
        # Quality User can't unlink the quality alert stage
        with self.assertRaises(AccessError):
            self.quality_alert_stage.with_user(self.quality_user).unlink()

        # Quality User can see the quality measure
        self.quality_measure.with_user(self.quality_user).read()
        # Quality User can't edit the quality measure
        with self.assertRaises(AccessError):
            self.quality_measure.with_user(self.quality_user).write({
                'name': 'New Measure'
            })
        # Quality User can't create the quality measure
        with self.assertRaises(AccessError):
            self.env['quality.point.test_type'].with_user(self.quality_user).create({
                'name': 'New Measure 1',
                'technical_name': 'measure',
            })
        # Quality User can't delete the quality measure
        with self.assertRaises(AccessError):
            self.quality_measure.with_user(self.quality_user).unlink()

        # Quality User can see the quality reason
        self.quality_reason.with_user(self.quality_user).read()
        # Quality User can't edit the quality reason
        with self.assertRaises(AccessError):
            self.quality_reason.with_user(self.quality_user).write({
                'name': 'New Reason'
            })
        # Quality User can't create the quality reason
        with self.assertRaises(AccessError):
            self.env['quality.reason'].with_user(self.quality_user).create({
                'name': 'New Reason 1',
            })
        # Quality User can't delete the quality reason
        with self.assertRaises(AccessError):
            self.quality_reason.with_user(self.quality_user).unlink()

        # Quality User can create the quality action
        quality_action = self.env['quality.action'].with_context(tracking_disable=True).with_user(self.quality_user).create({
            'name': 'New Action 1',
        })
        # Quality User can see the quality action
        quality_action.with_user(self.quality_user).read()
        # Quality User can edit the quality action
        quality_action.with_user(self.quality_user).write({
            'name': 'New Action'
        })
        # Quality User can't delete the quality action
        with self.assertRaises(AccessError):
            quality_action.with_user(self.quality_user).unlink()

        # Quality User can create the quality corrective action
        corrective_action = self.env['quality.alert.corrective.action'].with_context(tracking_disable=True).with_user(self.quality_user).create({
            'quality_action_id': quality_action.id,
            'quality_alert_id': quality_alert.id,
            'deadline': datetime(2021, 10, 15, 12, 0)
        })
        # Quality User can see the quality corrective action
        corrective_action.with_user(self.quality_user).read()
        # Quality User can edit the quality corrective action
        corrective_action.with_user(self.quality_user).write({
            'deadline': datetime(2021, 9, 15, 12, 0)
        })
        # Quality User can't delete the quality corrective action
        with self.assertRaises(AccessError):
            corrective_action.with_user(self.quality_user).unlink()

        # Quality User can create the quality preventive action
        preventive_action = self.env['quality.alert.preventive.action'].with_context(tracking_disable=True).with_user(self.quality_user).create({
            'quality_action_id': quality_action.id,
            'quality_alert_id': quality_alert.id,
            'deadline': datetime(2021, 10, 15, 12, 0)
        })
        # Quality User can see the quality preventive action
        preventive_action.with_user(self.quality_user).read()
        # Quality User can edit the quality preventive action
        preventive_action.with_user(self.quality_user).write({
            'deadline': datetime(2021, 9, 15, 12, 0)
        })
        # Quality User can't delete the quality preventive action
        with self.assertRaises(AccessError):
            preventive_action.with_user(self.quality_user).unlink()

        # Quality User can create the quality alert action
        alert_action = self.env['quality.alert.action'].with_user(self.quality_user).create({
            'quality_action_id': quality_action.id,
            'quality_alert_id': quality_alert.id,
            'deadline': datetime(2021, 10, 15, 12, 0)
        })
        # Quality User can see the quality alert action
        alert_action.with_user(self.quality_user).read()
        # Quality User can edit the quality alert action
        alert_action.with_user(self.quality_user).write({
            'deadline': datetime(2021, 9, 15, 12, 0)
        })
        # Quality User can't delete the quality alert action
        with self.assertRaises(AccessError):
            alert_action.with_user(self.quality_user).unlink()

    def test_11_quality_manager(self):
        # Quality Manager can create the quality check
        quality_check = self.env['quality.check'].with_context(tracking_disable=True).with_user(self.quality_manager).create({
            'product_id': self.quality_point_measure.product_id.id,
            'team_id': self.quality_point_measure.team_id.id,
            'checked_quantity': 80.00
        })
        # Quality Manager can see the quality check
        quality_check.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality check
        quality_check.with_user(self.quality_manager).write({
            'checked_quantity': 90.00
        })
        # Quality Manager can delete the quality check
        quality_check.with_user(self.quality_manager).unlink()

        # Quality Manager can see the quality point
        self.quality_point_measure.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality check
        self.quality_point_measure.with_user(self.quality_manager).write({
            'name': 'New Point'
        })
        # Quality Manager can create the quality check
        point_1 = self.env['quality.point'].with_context(tracking_disable=True).with_user(self.quality_manager).create({
            'product_tmpl_id': self.product_tmpl_a.id,
            'test_type_id': self.measure_type.id,
            'team_id': self.team.id,
        })

        # Quality Manager can see the quality tag
        self.quality_tag.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality tag
        self.quality_tag.with_user(self.quality_manager).write({
            'name': 'New Tag'
        })
        # Quality Manager can create the quality tag
        self.env['quality.tag'].with_user(self.quality_manager).create({
            'name': 'New Tag 1',
        })
        # Quality Manager can delete the quality tag
        self.quality_tag.with_user(self.quality_manager).unlink()

        # Quality Manager can see the quality reason
        self.quality_reason.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality reason
        self.quality_reason.with_user(self.quality_manager).write({
            'name': 'New Reason'
        })
        # Quality Manager can create the quality reason
        self.env['quality.reason'].with_user(self.quality_manager).create({
            'name': 'New Reason 1',
        })
        # Quality Manager can delete the quality reason
        self.quality_reason.with_user(self.quality_manager).unlink()

        # Quality Manager can create the quality alert
        quality_alert = self.env['quality.alert'].with_context(tracking_disable=True).with_user(self.quality_manager).create({
            'product_tmpl_id': self.product_tmpl_a.id,
            'team_id': self.quality_point_measure.team_id.id,
            'stage_id': self.quality_alert_stage.id
        })
        # Quality Manager can see the quality alert
        quality_alert.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality alert
        quality_alert.with_user(self.quality_manager).write({
            'name': 'New Alert 1'
        })

        # Quality Manager can create the quality action
        quality_action = self.env['quality.action'].with_context(tracking_disable=True).with_user(self.quality_manager).create({
            'name': 'New Action 1',
        })
        # Quality Manager can see the quality action
        quality_action.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality action
        quality_action.with_user(self.quality_manager).write({
            'name': 'New Action'
        })

        # Quality Manager can create the quality corrective action
        corrective_action = self.env['quality.alert.corrective.action'].with_context(tracking_disable=True).with_user(self.quality_manager).create({
            'quality_action_id': quality_action.id,
            'quality_alert_id': quality_alert.id,
            'deadline': datetime(2021, 10, 15, 12, 0)
        })
        # Quality Manager can see the quality corrective action
        corrective_action.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality corrective action
        corrective_action.with_user(self.quality_manager).write({
            'deadline': datetime(2021, 9, 15, 12, 0)
        })
        # Quality Manager can delete the quality corrective action
        corrective_action.with_user(self.quality_manager).unlink()

        # Quality Manager can create the quality preventive action
        preventive_action = self.env['quality.alert.preventive.action'].with_context(tracking_disable=True).with_user(self.quality_manager).create({
            'quality_action_id': quality_action.id,
            'quality_alert_id': quality_alert.id,
            'deadline': datetime(2021, 10, 15, 12, 0)
        })
        # Quality Manager can see the quality preventive action
        preventive_action.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality preventive action
        preventive_action.with_user(self.quality_manager).write({
            'deadline': datetime(2021, 9, 15, 12, 0)
        })
        # Quality Manager can delete the quality preventive action
        preventive_action.with_user(self.quality_manager).unlink()

        # Quality Manager can create the quality alert action
        alert_action = self.env['quality.alert.action'].with_user(self.quality_manager).create({
            'quality_action_id': quality_action.id,
            'quality_alert_id': quality_alert.id,
            'deadline': datetime(2021, 10, 15, 12, 0)
        })
        # Quality Manager can see the quality alert action
        alert_action.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality alert action
        alert_action.with_user(self.quality_manager).write({
            'deadline': datetime(2021, 9, 15, 12, 0)
        })
        # Quality Manager can delete the quality alert action
        alert_action.with_user(self.quality_manager).unlink()

        # Quality Manager can delete the quality alert
        quality_alert.with_user(self.quality_manager).unlink()

        # Quality Manager can delete the quality action
        quality_action.with_user(self.quality_manager).unlink()

        # Quality Manager can delete the quality point
        self.quality_point_measure.with_user(self.quality_manager).unlink()

        # Quality Manager can see the quality alert stage
        self.quality_alert_stage.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality alert stage
        self.quality_alert_stage.with_user(self.quality_manager).write({
            'name': 'New Alert Stage'
        })
        # Quality Manager can create the quality alert stage
        self.env['quality.alert.stage'].with_user(self.quality_manager).create({
            'name': 'New Alert Stage 1',
        })
        # Quality Manager can delete the quality alert stage
        self.quality_alert_stage.with_user(self.quality_manager).unlink()

        # Quality Manager can see the quality team
        self.team.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality team
        self.team.with_user(self.quality_manager).write({
            'name': 'New Team'
        })
        # Quality Manager can create the quality team
        team_1 = self.env['quality.alert.team'].with_user(self.quality_manager).create({
            'name': 'New Team 1',
            'alias_id': self.env.ref('to_quality.mail_alias_quality_alert').id
        })

        # Quality Manager can see the quality measure
        self.quality_measure.with_user(self.quality_manager).read()
        # Quality Manager can edit the quality measure
        self.quality_measure.with_user(self.quality_manager).write({
            'name': 'New Measure'
        })
        # Quality Manager can create the quality measure
        quality_measure_1 = self.env['quality.point.test_type'].with_user(self.quality_manager).create({
            'name': 'New Measure 1',
            'technical_name': 'measure',
        })
        # Quality Manager can delete the quality measure
        quality_measure_1.with_user(self.quality_manager).unlink()
