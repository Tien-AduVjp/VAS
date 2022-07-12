from dateutil import parser
import json

from odoo.exceptions import ValidationError
from unittest.mock import patch
from odoo.tests.common import tagged, Form
from .common import ZoomCommon


@tagged('post_install', '-at_install')
class TestZoomCalendar(ZoomCommon):

    def test_001_create_zoom_calendar(self,):
        with patch('%s.get_meetings' % (self.path_zoom_api_v2), self._mock_request_get_meetings):
            with patch('%s.create_meeting' % (self.path_zoom_api_v2), self._mock_request_create_meeting):
                calendar_form = Form(self.env['calendar.event'])
                calendar_form.name = 'Hop noi bo'
                calendar_form.start = '2021-08-08 10:00:00'
                calendar_form.allday = False
                calendar_form.stop = '2021-08-08 11:00:00'
                calendar_form.is_zoom_meeting = True
                zoom_calendar = calendar_form.save()

        self.assertRecordValues(
            zoom_calendar,
            [{
                'zoom_meeting_id': 'id',
                'zoom_meeting_attendee_url': 'join_url',
                'zoom_meeting_start_url': 'start_url',
                'zoom_name': 'Hop noi bo',
                'zoom_start_datetime': parser.parse(calendar_form.start),
                'zoom_duration': calendar_form.duration * 60,
                }]
            )

        # Test delete zoom meeting when disabling Is Zoom Meeting on calendar event
        with patch('%s.delete_meeting' % (self.path_zoom_api_v2), self._mock_request_delete_meeting):
            zoom_calendar.is_zoom_meeting = False

        self.assertRecordValues(
            zoom_calendar,
            [{
                'zoom_meeting_id': False,
                'zoom_meeting_attendee_url': False,
                'zoom_meeting_start_url': False,
                
                }]
            )

    def test_002_create_zoom_calendar(self,):
        with patch('%s.get_meetings' % (self.path_zoom_api_v2), self._mock_request_get_meetings):
            with patch('%s.create_meeting' % (self.path_zoom_api_v2), self._mock_request_create_meeting_fc002):
                calendar_form = Form(self.env['calendar.event'])
                calendar_form.name = 'Hop noi bo'
                calendar_form.start = '2021-08-08 10:00:00'
                calendar_form.allday = False
                calendar_form.stop = '2021-08-08 11:00:00'
                calendar_form.is_zoom_meeting = True
                calendar_form.zoom_setting = True
                calendar_form.zoom_setting_join_before_host = True
                calendar_form.zoom_setting_mute_upon_entry = True
                calendar_form.zoom_setting_approval_type = '1'
                calendar_form.zoom_setting_auto_recording = 'none'
                zoom_calendar = calendar_form.save()

        self.assertRecordValues(
            zoom_calendar,
            [{
                'zoom_meeting_id': 'id',
                'zoom_meeting_attendee_url': 'join_url',
                'zoom_meeting_start_url': 'start_url',
                'zoom_name': 'Hop noi bo',
                'zoom_start_datetime': parser.parse(calendar_form.start),
                'zoom_duration': calendar_form.duration * 60,
                }]
            )

    def _mock_request_create_meeting_fc002(self, user_id, data):
        response = self._mock_request_create_meeting(user_id, data)
        self.assertEqual('settings' in data, True, "to_zoom_calendar: error param create zoom calendar")
        settings = data['settings']
        self.assertEqual(settings['join_before_host'], True, "to_zoom_calendar: error param create zoom calendar")
        self.assertEqual(settings['mute_upon_entry'], True, "to_zoom_calendar: error param create zoom calendar")
        self.assertEqual(settings['approval_type'], '1', "to_zoom_calendar: error param create zoom calendar")
        self.assertEqual(settings['auto_recording'], 'none', "to_zoom_calendar: error param create zoom calendar")
        content = {
            'id': 'id',
            'start_url': 'start_url',
            'join_url': 'join_url',
            'setting': {
                'join_before_host': True,
                'mute_upon_entry': True,
                'mute_upon_entry': True,
                'approval_type': '1',
                'auto_recording': 'none'
            }
        }
        response._content = str.encode(json.dumps(content))
        return response

    def test_003_create_zoom_calendar(self,):
        with patch('%s.get_meetings' % (self.path_zoom_api_v2), self._mock_request_get_meetings):
            with patch('%s.create_meeting' % (self.path_zoom_api_v2), self._mock_request_create_meeting_fc003):
                calendar_form = Form(self.env['calendar.event'])
                calendar_form.name = 'Hop noi bo'
                calendar_form.start = '2021-08-08 10:00:00'
                calendar_form.allday = False
                calendar_form.stop = '2021-08-08 11:00:00'
                calendar_form.is_zoom_meeting = True
                calendar_form.recurrency = True
                calendar_form.rrule_type = 'daily'
                calendar_form.interval = 1
                calendar_form.end_type = 'count'
                calendar_form.count = 3
                zoom_calendar = calendar_form.save()

        self.assertRecordValues(
            zoom_calendar,
            [{
                'zoom_meeting_id': 'id',
                'zoom_meeting_attendee_url': 'join_url',
                'zoom_meeting_start_url': 'start_url',
                'zoom_name': 'Hop noi bo',
                'zoom_start_datetime': parser.parse(calendar_form.start),
                'zoom_duration': calendar_form.duration * 60,
                'zoom_recurrency': True,
                'zoom_rrule_type': 'daily',
                'zoom_interval': 1,
                'zoom_end_type': 'count',
                'zoom_count': 3,
                }]
            )

    def _mock_request_create_meeting_fc003(self, user_id, data):
        response = self._mock_request_create_meeting(user_id, data)
        self.assertEqual('recurrence' in data, True, "to_zoom_calendar: error param create zoom calendar")
        recurrence = data['recurrence']
        self.assertEqual(recurrence['repeat_interval'], 1, "to_zoom_calendar: error param create zoom calendar")
        self.assertEqual(recurrence['type'], 1, "to_zoom_calendar: error param create zoom calendar")
        self.assertEqual(recurrence['end_times'], 3, "to_zoom_calendar: error param create zoom calendar")
        return response

    def test_007_unlink_zoom_calendar(self):
        with patch('%s.get_meetings' % (self.path_zoom_api_v2), self._mock_request_get_meetings):
            with patch('%s.create_meeting' % (self.path_zoom_api_v2), self._mock_request_create_meeting):
                calendar_form = Form(self.env['calendar.event'])
                calendar_form.name = 'Hop noi bo'
                calendar_form.start = '2021-08-08 10:00:00'
                calendar_form.allday = False
                calendar_form.stop = '2021-08-08 11:00:00'
                calendar_form.is_zoom_meeting = True
                zoom_calendar = calendar_form.save()
        with patch('%s.delete_meeting' % (self.path_zoom_api_v2), self._mock_request_delete_meeting):
            zoom_calendar.unlink()

    def test_1001_create_zoom_calendar_fail(self,):
        with patch('%s.get_meetings' % (self.path_zoom_api_v2), self._mock_request_get_meetings):
            with patch('%s.create_meeting' % (self.path_zoom_api_v2), self._mock_request_create_meeting_fail):
                calendar_form = Form(self.env['calendar.event'])
                calendar_form.name = 'Hop noi bo'
                calendar_form.start = '2021-08-08 10:00:00'
                calendar_form.allday = False
                calendar_form.stop = '2021-08-08 11:00:00'
                calendar_form.is_zoom_meeting = True
                with self.assertRaises(ValidationError):
                    calendar_form.save()

    def test_1002_write_zoom_calendar(self,):
        zoom_calendar = self._create_zoom_calendar()
        with patch('%s.update_meeting' % (self.path_zoom_api_v2), self._mock_request_write_zoom):
            with patch('%s.get_meeting' % (self.path_zoom_api_v2), self._mock_request_get_meeting):
                zoom_calendar.write({'zoom_name': 'test_zoom_name'})
        self.assertEqual(zoom_calendar.zoom_name, 'test_zoom_name', "to_zoom_calendar: error write zoom meeting")

    def test_1002_write_zoom_calendar_fail(self,):
        zoom_calendar = self._create_zoom_calendar()
        old_zoom_name = zoom_calendar.zoom_name
        with patch('%s.update_meeting' % (self.path_zoom_api_v2), self._mock_request_write_zoom_fail):
            with self.assertRaises(ValidationError):
                zoom_calendar.write({'zoom_name': 'test_zoom_name'})
        self.assertEqual(zoom_calendar.zoom_name, old_zoom_name, "to_zoom_calendar: error write zoom meeting")

    def test_1003_unlink_zoom_calendar_fail(self,):
        zoom_calendar = self._create_zoom_calendar()
        with patch('%s.delete_meeting' % (self.path_zoom_api_v2), self._mock_request_delete_meeting_fail):
            with self.assertRaises(ValidationError):
                zoom_calendar.unlink()
                self.assertTrue(zoom_calendar.exists())
