from datetime import datetime, timedelta
from unittest.mock import patch

from odoo.tests import tagged
from odoo.exceptions import ValidationError

from .test_helpdesk_common import SavepointCase


@tagged('post_install', '-at_install')
class TestHelpdesk(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHelpdesk, cls).setUpClass()
        cls.new_stage = cls.env.ref('viin_helpdesk.helpdesk_stage_new')
        cls.assigned = cls.env.ref('viin_helpdesk.helpdesk_stage_assigned')
        cls.resolved_stage = cls.env.ref('viin_helpdesk.helpdesk_stage_resolved')
        cls.team_general = cls.env.company.default_helpdesk_team_id
        cls.sla_assigned = cls.env['helpdesk.sla'].create({
            'name': '10h',
            'team_id': cls.env.company.default_helpdesk_team_id.id,
            'stage_id': cls.assigned.id,
            'time_hours': 5,
        })
        cls.sla_resolved = cls.env['helpdesk.sla'].create({
            'name': '10h',
            'team_id': cls.env.company.default_helpdesk_team_id.id,
            'stage_id': cls.resolved_stage.id,
            'time_hours': 10,
        })
        cls.env.company.default_helpdesk_team_id.stage_ids = [(6, 0, [cls.new_stage.id, cls.assigned.id, cls.resolved_stage.id])]

    def test_sla_overlap(self):
        helpdesk_sla = self.env['helpdesk.sla'].create({
            'name': 'Sla Test',
            'team_id': self.team_general.id,
            'stage_id': self.new_stage.id,
        })
        with self.assertRaises(ValidationError):
            helpdesk_sla.copy()

    def test_sla_status_ongoing_reached(self):
        ticket_sla = self.env['helpdesk.ticket'].create({
            'name': 'Ticket Test Sla',
            'team_id': self.team_general.id,
        })

        # self.assertEqual(ticket_sla.sla_line_ids.status, 'ongoing')
        self.assertRecordValues(ticket_sla.sla_line_ids,
            [
                {
                    'status': 'ongoing',
                },
                {
                    'status': 'ongoing',
                }
            ])

        ticket_sla.stage_id = self.resolved_stage
        self.assertRecordValues(ticket_sla.sla_line_ids,
            [
                {
                    'status': 'reached',
                    'exceeded_days': 0
                },
                {
                    'status': 'reached',
                    'exceeded_days': 0
                }
            ])

    def test_sla_status_failed(self):
        ticket_sla = self.env['helpdesk.ticket'].create({
            'name': 'Ticket Test Sla Failed',
            'team_id': self.team_general.id,
        })
        with patch('odoo.fields.Datetime.now', return_value=datetime.now() + timedelta(days=100)), self.env.cr.savepoint():
            ticket_sla.stage_id = self.resolved_stage
        sla_lines = ticket_sla.sla_line_ids
        self.assertRecordValues(ticket_sla.sla_line_ids,
            [
                {
                    'status': 'failed',
                    'exceeded_days': ticket_sla.team_id.resource_calendar_id.get_work_duration_data(
                        sla_lines[0].deadline_datetime, sla_lines[0].reached_datetime, compute_leaves=True)['days']
                },
                {
                    'status': 'failed',
                    'exceeded_days': ticket_sla.team_id.resource_calendar_id.get_work_duration_data(
                        sla_lines[1].deadline_datetime, sla_lines[1].reached_datetime, compute_leaves=True)['days']
                }
            ])

    def test_sla_status_1(self):
        """
        Case: Kiểm tra trường hợp chuyển ticket sang giai đoạn cuối cùng
        Input:
            + Ticket có 3 giai đoạn, có 2 sla ở giai đoạn 2 và 3
            + Thực hiện chuyển ticket sang giai đoạn 3, giai đoạn 2 chưa có thời gian đạt được
        Output: Thời gian đạt được của giai đoạn 2 giống giai đoạn 3
        """
        ticket_sla = self.env['helpdesk.ticket'].create({
            'name': 'Ticket Test Sla Failed',
            'team_id': self.team_general.id,
        })
        ticket_sla.stage_id = self.resolved_stage
        sla_lines = ticket_sla.sla_line_ids
        self.assertEqual(sla_lines[0].reached_datetime, sla_lines[1].reached_datetime)

    def test_sla_status_2(self):
        """
        Case: Kiểm tra trường hợp chuyển ticket sang giai đoạn cuối cùng
        Input:
            + Ticket có 3 giai đoạn, có 2 sla ở giai đoạn 2 và 3
            + Thực hiện chuyển ticket sang giai đoạn 2, sau đó chuyển sang giai đoạn 3
        Output: Thời gian đạt được của giai đoạn 2 khác giai đoạn 3
        """
        ticket_sla = self.env['helpdesk.ticket'].create({
            'name': 'Ticket Test Sla Failed',
            'team_id': self.team_general.id,
        })
        ticket_sla.stage_id = self.resolved_stage
        ticket_sla.stage_id = self.assigned
        sla_lines = ticket_sla.sla_line_ids
        self.assertNotEqual(sla_lines[0].reached_datetime, sla_lines[1].reached_datetime)
