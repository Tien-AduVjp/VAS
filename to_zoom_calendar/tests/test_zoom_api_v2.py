from unittest import mock
from odoo.tests import SavepointCase, tagged
from odoo.exceptions import ValidationError

ZOOM_API_URL = 'https://api.zoom.us/v2/'


@tagged('post_install', '-at_install')
class TestZoomAPIV2(SavepointCase):
    def setUp(self):
        super(TestZoomAPIV2, self).setUp()
        self.zoom_api_key = 'test-key'
        self.zoom_secret_key = 'test-secret'

    def test_unconfigured_zoom_keys(self):
        """
        Test unconfigured zoom public and private keys
        """

        self.env.company.zoom_api_key = ''
        self.env.company.zoom_secret_key = 'test-secret'
        self.assertRaises(ValidationError, self.env['zoom.apiv2'].generate_JWT_key)

        self.env.company.zoom_api_key = 'test-key'
        self.env.company.zoom_secret_key = ''
        self.assertRaises(ValidationError, self.env['zoom.apiv2'].generate_JWT_key)

    @mock.patch('odoo.addons.to_zoom_calendar.models.zoom_api_v2.fields')
    @mock.patch('odoo.addons.to_zoom_calendar.models.zoom_api_v2.jwt')
    def test_generate_JWT_key_with_correct_params(self, mock_jwt, mock_fields):
        """
        Test generate JWT key with correct params
        """

        self.env.company.zoom_api_key = self.zoom_api_key
        self.env.company.zoom_secret_key = self.zoom_secret_key
        mock_jwt.encode.return_value = b'hello word'
        mock_fields.Datetime.now().timestamp().__int__.return_value = 1577811600  # 2020-01-01
        result = self.env['zoom.apiv2'].generate_JWT_key()

        mock_jwt.encode.assert_called_once_with(
            {
                'iss': self.zoom_api_key,
                'exp': 1577811660
            },
            self.zoom_secret_key,
            algorithm='HS256'
        )
        self.assertEqual(result, 'hello word', "to_zoom_calendar: wrong result of generate_JWT_key")

    @mock.patch('odoo.addons.to_zoom_calendar.models.zoom_api_v2.fields')
    def test_generate_JWT_key(self, mock_fields):
        """
        Test generate JWT key
        """

        self.env.company.zoom_api_key = self.zoom_api_key
        self.env.company.zoom_secret_key = self.zoom_secret_key
        mock_fields.Datetime.now().timestamp().__int__.return_value = 1577811600  # 2020-01-01

        self.assertEqual(
            self.env['zoom.apiv2'].generate_JWT_key(),
            'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ0ZXN0LWtleSIsImV4cCI6MTU3NzgxMTY2MH0.9L9W5KYABElUPN9uZtft1zg6ZYVGfblHCakrzaKdT1E'
        )

    def test_send_invalid_request(self):
        """
        Test send invalid request
        """

        # Prepare test data
        url_segment = 'test'
        url = ZOOM_API_URL + url_segment
        method = 'TEST'

        # Check return if invalid method
        with mock.patch.object(type(self.env['zoom.apiv2']), 'generate_JWT_key') as mock_generate_JWT_key:
            mock_generate_JWT_key.return_value = '123456789'
            self.assertFalse(self.env['zoom.apiv2'].send_request(url_segment=url_segment, method=method))

    @mock.patch('odoo.addons.to_zoom_calendar.models.zoom_api_v2.requests')
    def test_send_get_request(self, mock_requests):
        """
        Test send GET request
        """

        # Prepare test data
        url_segment = 'test'
        url = ZOOM_API_URL + url_segment
        method = 'GET'

        # Set return value to test
        mock_requests.get.return_value = 'hello word'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'generate_JWT_key') as mock_generate_JWT_key:
            mock_generate_JWT_key.return_value = '123456789'
            result = self.env['zoom.apiv2'].send_request(url_segment=url_segment, method=method)

        # Check if requests is called with correct params
        mock_requests.get.assert_called_once_with(
            url,
            headers={
                'Authorization': 'Bearer 123456789',
                'Content-Type': 'application/json'
            }
        )
        self.assertEqual(result, 'hello word', "to_zoom_calendar: wrong result of send_get_request")

    @mock.patch('odoo.addons.to_zoom_calendar.models.zoom_api_v2.requests')
    def test_send_delete_request(self, mock_requests):
        """
        Test send DELETE request
        """

        # Prepare test data
        url_segment = 'test'
        url = ZOOM_API_URL + url_segment
        method = 'DELETE'

        # Set return value to test
        mock_requests.delete.return_value = 'hello word'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'generate_JWT_key') as mock_generate_JWT_key:
            mock_generate_JWT_key.return_value = '123456789'
            result = self.env['zoom.apiv2'].send_request(url_segment=url_segment, method=method)

        # Check if requests is called with correct params
        mock_requests.delete.assert_called_once_with(
            url,
            headers={
                'Authorization': 'Bearer 123456789',
                'Content-Type': 'application/json'
            }
        )
        self.assertEqual(result, 'hello word', "to_zoom_calendar: wrong result of send_delete_request")

    @mock.patch('odoo.addons.to_zoom_calendar.models.zoom_api_v2.requests')
    def test_send_patch_request(self, mock_requests):
        """
        Test send PATCH request
        """

        # Prepare test data
        data = {'name': 'John'}
        url_segment = 'test'
        url = ZOOM_API_URL + url_segment
        method = 'PATCH'

        # Set return value to test
        mock_requests.patch.return_value = 'hello word'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'generate_JWT_key') as mock_generate_JWT_key:
            mock_generate_JWT_key.return_value = '123456789'
            result = self.env['zoom.apiv2'].send_request(url_segment=url_segment, data=data, method=method)

        # Check if requests is called with correct params
        mock_requests.patch.assert_called_once_with(
            url,
            json=data,
            headers={
                'Authorization': 'Bearer 123456789',
                'Content-Type': 'application/json'
            }
        )
        self.assertEqual(result, 'hello word', "to_zoom_calendar: wrong result of request")

    @mock.patch('odoo.addons.to_zoom_calendar.models.zoom_api_v2.requests')
    def test_send_put_request(self, mock_requests):
        """
        Test send PUT request
        """

        # Prepare test data
        data = {'name': 'John'}
        url_segment = 'test'
        url = ZOOM_API_URL + url_segment
        method = 'PUT'

        # Set return value to test
        mock_requests.put.return_value = 'hello word'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'generate_JWT_key') as mock_generate_JWT_key:
            mock_generate_JWT_key.return_value = '123456789'
            result = self.env['zoom.apiv2'].send_request(url_segment=url_segment, data=data, method=method)

        # Check if requests is called with correct params
        mock_requests.put.assert_called_once_with(
            url,
            json=data,
            headers={
                'Authorization': 'Bearer 123456789',
                'Content-Type': 'application/json'
            }
        )
        self.assertEqual(result, 'hello word', "to_zoom_calendar: wrong result of send_put_request")

    @mock.patch('odoo.addons.to_zoom_calendar.models.zoom_api_v2.requests')
    def test_send_post_request(self, mock_requests):
        """
        Test send POST request
        """

        # Prepare test data
        data = {'name': 'John'}
        url_segment = 'test'
        url = ZOOM_API_URL + url_segment
        method = 'POST'

        # Set return value to test
        mock_requests.post.return_value = 'hello word'
        with mock.patch.object(type(self.env['zoom.apiv2']), 'generate_JWT_key') as mock_generate_JWT_key:
            mock_generate_JWT_key.return_value = '123456789'
            result = self.env['zoom.apiv2'].send_request(url_segment=url_segment, data=data, method=method)

        # Check if requests is called with correct params
        mock_requests.post.assert_called_once_with(
            url,
            json=data,
            headers={
                'Authorization': 'Bearer 123456789',
                'Content-Type': 'application/json'
            }
        )
        self.assertEqual(result, 'hello word', "to_zoom_calendar: wrong result of send_post_request")

    def test_get_meeting(self):
        """
        Check if params on send_request is correct when call
        """
        meeting_id = 10
        url_segment = 'meetings/10'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'send_request') as mocked:
            self.env['zoom.apiv2'].get_meeting(meeting_id)
            mocked.assert_called_with(url_segment, method='GET')

    def test_get_meetings(self):
        """
        Check if params on send_request is correct when call
        """
        user_id = 10
        page_size = 30
        page_number = 1
        url_segment = '/users/10/meetings?type=scheduled&page_size=30&page_number=1'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'send_request') as mocked:
            self.env['zoom.apiv2'].get_meetings(user_id, page_size, page_number)
            mocked.assert_called_with(url_segment, method='GET')

    def test_create_meeting(self):
        """
        Check if params on send_request is correct when call
        """
        user_id = 1
        test_data = 'test'
        url_segment = 'users/1/meetings'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'send_request') as mocked:
            self.env['zoom.apiv2'].create_meeting(user_id, test_data)
            mocked.assert_called_with(url_segment, data=test_data, method='POST')

    def test_update_meeting(self):
        """
        Check if params on send_request is correct when call
        """
        meeting_id = 5
        test_data = 'test'
        url_segment = 'meetings/5'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'send_request') as mocked:
            self.env['zoom.apiv2'].update_meeting(meeting_id, test_data)
            mocked.assert_called_with(url_segment, data=test_data, method='PATCH')

    def test_delete_meeting(self):
        """
        Check if params on send_request is correct when call
        """
        meeting_id = 5
        url_segment = 'meetings/5'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'send_request') as mocked:
            self.env['zoom.apiv2'].delete_meeting(meeting_id)
            mocked.assert_called_with(url_segment, method='DELETE')

    def test_get_user(self):
        """
        Check if params on send_request is correct when call
        """
        user_id = 5
        url_segment = 'users/5'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'send_request') as mocked:
            self.env['zoom.apiv2'].get_user(user_id)
            mocked.assert_called_with(url_segment, method='GET')

    def test_create_user(self):
        """
        Check if params on send_request is correct when call
        """
        data = 'test_data'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'send_request') as mocked:
            self.env['zoom.apiv2'].create_user(data)
            mocked.assert_called_with('users', data=data, method='POST')

    def test_update_user(self):
        """
        Check if params on send_request is correct when call
        """
        user_id = 5
        data = 'test_data'
        url_segment = 'users/5'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'send_request') as mocked:
            self.env['zoom.apiv2'].update_user(user_id, data)
            mocked.assert_called_with(url_segment, data=data, method='PATCH')

    def test_delete_user(self):
        """
        Check if params on send_request is correct when call
        """
        user_id = 5
        url_segment = 'users/5'

        with mock.patch.object(type(self.env['zoom.apiv2']), 'send_request') as mocked:
            self.env['zoom.apiv2'].delete_user(user_id)
            mocked.assert_called_with(url_segment, method='DELETE')

    def test_get_report_users(self):
        """
        Check if params on send_request is correct when call
        """
        date_from = '2020-01-01'
        date_to = '2020-05-01'
        page_size = 30
        page_number = 1

        url_segment = '/report/users?type=active&from=%s&to=%s&page_size=%s&page_number=%s' % (date_from, date_to, page_size, page_number)

        with mock.patch.object(type(self.env['zoom.apiv2']), 'send_request') as mocked:
            self.env['zoom.apiv2'].get_report_users(date_from, date_to, page_size=page_size, page_number=page_number)
            mocked.assert_called_with(url_segment, method='GET')
