import json

from requests.models import Response
from unittest.mock import patch
from odoo.tests.common import SingleTransactionCase, Form


class ZoomCommon(SingleTransactionCase):

    def setUp(self):
        super(ZoomCommon, self).setUp()
        self.user_admin = self.env.ref('base.user_admin')
        self.user_demo = self.env.ref('base.user_demo')
        self.setup_config_zoom_calendar()
        self.path_zoom_api_v2 = 'odoo.addons.to_zoom_calendar.models.zoom_api_v2.ZoomAPIv2'
        with patch('%s.create_user' % (self.path_zoom_api_v2), self._mock_request_create_user):
            self.user_zoom = self.env['zoom.user'].create(
                self._vals_create_zoom_user('zoom_user_test_case_00001'))

    def setup_config_zoom_calendar(self):
        ConfigParams = self.env['ir.config_parameter'].sudo()
        ConfigParams.set_param('company_id.zoom_api_key', 'firebase')
        ConfigParams.set_param('company_id.zoom_secret_key', 'test_auth_key')
        self.env.company.zoom_api_key = 'firebase'
        self.env.company.zoom_secret_key = 'test_auth_key'

    def _mock_request_create_user(self, data):
        self.assertEqual('user_info' in data, True, "to_zoom_calendar: error request pargram")
        user_info = data['user_info']
        self.assertEqual('email' in user_info, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('first_name' in user_info, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('last_name' in user_info, True, "to_zoom_calendar: error request pargram")
        return self._response_request(201)

    def _mock_request_create_user_fail(self, data):
        self.assertEqual('user_info' in data, True, "to_zoom_calendar: error request pargram")
        user_info = data['user_info']
        self.assertEqual('email' in user_info, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('first_name' in user_info, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('last_name' in user_info, True, "to_zoom_calendar: error request pargram")
        response = self._response_request(400)
        content = {'message': 'Create Zoom user failed'}
        response._content = str.encode(json.dumps(content))
        return response

    def _mock_request_update_user(self, user_id, data):
        return self._response_request(204)

    def _mock_request_update_user_fail(self, user_id, data):
        content = {'message': 'Error Zoom user: update user fail'}
        return self._response_request(400, content)

    def _mock_request_delete_user(self, user_id):
        return self._response_request(204)

    def _mock_request_delete_user_fail(self, user_id):
        content = {'message': 'Error Zoom user: delete user fail'}
        return self._response_request(400, content)

    def _vals_create_zoom_user(self, name, company_id=False):
        company_id = company_id or self.env.ref('base.main_company').id
        return {
            'company_id': company_id,
            'zoom_email': '%s@example1.com' % (name),
            'zoom_first_name': 'zoom_first_name_%s' % (name),
            'zoom_last_name': 'zoom_last_name_%s' % (name),
        }

    def _mock_request_get_meetings(self, user_id, page_size=30, page_number=1):
        zoom_users = self.env['zoom.user'].search([]).mapped('zoom_email')
        self.assertEqual(user_id in zoom_users, True, "to_zoom_calendar: error request pargram")
        response = self._response_request(200)
        # _content has 5 meetings:
        # '2021-09-16T02:30:00Z', 30
        # '2021-09-17T02:30:00Z', 30
        # '2021-09-17T03:20:52Z', 30
        # '2021-09-18T02:30:00Z', 30
        # '2021-09-18T03:00:00Z', 30
        # '2021-10-18T14:30:00Z', 30
        # timezonge = 'Europe/Brussels'
        response._content = b'{"page_count":1,"page_number":1,"page_size":30,"total_records":6,"meetings":[{"uuid":"flQKx90FRLat8ibVWqzUeg==","id":89085866160,"host_id":"V0SfC9hTRO-8g84v91GENw","topic":"1312344","type":2,"start_time":"2021-09-16T02:30:00Z","duration":30,"timezone":"Europe/Brussels","created_at":"2021-09-15T08:25:46Z","join_url":"https://us05web.zoom.us/j/89085866160?pwd=WDYwUWdvSVNCQ2JYMzhDWEFJbXNHQT09"},{"uuid":"/lDw6hw3Qm+FZ5VDFXSrBQ==","id":81705606625,"host_id":"V0SfC9hTRO-8g84v91GENw","topic":"111","type":2,"start_time":"2021-09-17T02:30:00Z","duration":30,"timezone":"Europe/Brussels","created_at":"2021-09-15T09:22:58Z","join_url":"https://us05web.zoom.us/j/81705606625?pwd=VWYwMkVndTU2SExFQWJEb1I2emI1UT09"},{"uuid":"A1LJu/aiRCiWg0VNV8DjXw==","id":84184967285,"host_id":"V0SfC9hTRO-8g84v91GENw","topic":"111","type":2,"start_time":"2021-09-17T03:20:52Z","duration":30,"timezone":"Europe/Brussels","created_at":"2021-09-17T03:20:51Z","join_url":"https://us05web.zoom.us/j/84184967285?pwd=UjJKSjM0Y2hqTE9BdWhyZGJFT3BvZz09"},{"uuid":"2Pd4nIfsQYmR35gz+ZWdOg==","id":85864760747,"host_id":"V0SfC9hTRO-8g84v91GENw","topic":"H\xe1\xbb\x8dp b\xc3\xa0n chi\xe1\xba\xbfn tranh th\xe1\xba\xbf gi\xe1\xbb\x9bi 3","type":2,"start_time":"2021-09-18T02:30:00Z","duration":30,"timezone":"Europe/Brussels","created_at":"2021-09-16T07:49:13Z","join_url":"https://us05web.zoom.us/j/85864760747?pwd=TWJtZ0NBRXpaV0hBL3QySWR1bmpoZz09"},{"uuid":"7nnntc9ESZ6NJr+TqMky9A==","id":81948124074,"host_id":"V0SfC9hTRO-8g84v91GENw","topic":"H\xe1\xbb\x8dp b\xc3\xa0n chi\xe1\xba\xbfn tranh th\xe1\xba\xbf gi\xe1\xbb\x9bi 4","type":2,"start_time":"2021-09-18T03:00:00Z","duration":30,"timezone":"Europe/Brussels","created_at":"2021-09-16T07:56:20Z","join_url":"https://us05web.zoom.us/j/81948124074?pwd=SDJIdHAxNVFxaXlnSUhXYXhKR1d0QT09"},{"uuid":"emJjuCi/RK+YvkY1Q3sv+A==","id":84817610417,"host_id":"V0SfC9hTRO-8g84v91GENw","topic":"Test Zoom Calendar","type":2,"start_time":"2021-10-18T14:30:00Z","duration":30,"timezone":"Europe/Brussels","created_at":"2021-09-17T03:32:41Z","join_url":"https://us05web.zoom.us/j/84817610417?pwd=K1E0K3VGZ1Z4YnE1ZCtmMXlsZFgwZz09"}]}'
        return response

    def _mock_request_get_meeting(self, meeting_id):
        content = {'join_url': 'join_url', 'start_url': 'start_url'}
        return self._response_request(200, content)

    def _mock_request_create_meeting(self, user_id, data):
        zoom_users = self.env['zoom.user'].search([]).mapped('zoom_email')
        self.assertEqual(user_id in zoom_users, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('password' in data, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('timezone' in data, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('topic' in data, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('type' in data, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('start_time' in data, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('duration' in data, True, "to_zoom_calendar: error request pargram")
        content = {'id': 'id', 'start_url': 'start_url', 'join_url': 'join_url'}
        return self._response_request(201, content)

    def _mock_request_create_meeting_fail(self, user_id, data):
        zoom_users = self.env['zoom.user'].search([]).mapped('zoom_email')
        self.assertEqual(user_id in zoom_users, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('password' in data, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('timezone' in data, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('topic' in data, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('type' in data, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('start_time' in data, True, "to_zoom_calendar: error request pargram")
        self.assertEqual('duration' in data, True, "to_zoom_calendar: error request pargram")
        content = {'message': 'Create Zoom failed'}
        return self._response_request(400, content)

    def _mock_request_write_zoom(self, meeting_id, data):
        return self._response_request(204)

    def _mock_request_write_zoom_fail(self, meeting_id, data):
        content = {'message': 'Error Zoom meetting: update meeting fail'}
        return self._response_request(400, content)

    def _mock_request_delete_meeting(self, meeting_id):
        self.assertEqual(meeting_id is not False, True, "to_zoom_calendar: error request pargram")
        return self._response_request(204)

    def _mock_request_delete_meeting_fail(self, meeting_id):
        self.assertEqual(meeting_id is not False, True, "to_zoom_calendar: error request pargram")
        content = {'message': 'Error Zoom meetting: delete meeting fail'}
        return self._response_request(400, content)

    def _response_request(self, status_code, content=False):
        response = Response()
        response.status_code = status_code
        response.reason = 'OK'
        response.url = 'https://api.zoom.us/v2/'
        if content:
            response._content = str.encode(json.dumps(content))
        return response

    def _create_zoom_calendar(self, start=False, stop=False):
        with patch('%s.get_meetings' % (self.path_zoom_api_v2), self._mock_request_get_meetings):
            with patch('%s.create_meeting' % (self.path_zoom_api_v2), self._mock_request_create_meeting):
                calendar_form = Form(self.env['calendar.event'])
                calendar_form.name = 'Hop noi bo'
                calendar_form.start = start or '2021-11-11 10:00:00'
                calendar_form.allday = False
                calendar_form.stop = stop or '2021-11-11 11:00:00'
                calendar_form.is_zoom_meeting = True
                zoom_calendar = calendar_form.save()
        return zoom_calendar
