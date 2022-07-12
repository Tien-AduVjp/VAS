
from odoo.exceptions import ValidationError
from unittest import mock
from odoo.tests.common import tagged


from .common import ZoomCommon


@tagged('post_install', '-at_install')
class TestZoomUser(ZoomCommon):
    def test_001_create_user(self):
        with mock.patch('%s.create_user' % (self.path_zoom_api_v2), self._mock_request_create_user):
            self.env['zoom.user'].create(self._vals_create_zoom_user('test_4'))
            zoom_new_user = self.env['zoom.user'].search([('zoom_email', '=', 'test_4@example1.com')])
            self.assertTrue(zoom_new_user.exists())

    def test_002_create_user_fail(self):
        with mock.patch('%s.create_user' % (self.path_zoom_api_v2), self._mock_request_create_user_fail):
            with self.assertRaises(ValidationError):
                self.env['zoom.user'].create(self._vals_create_zoom_user('test_fail_88888'))
                zoom_new_user = self.env['zoom.user'].search([
                    ('zoom_email', '=', 'test_fail_88888@example1.com')])
                self.assertFalse(zoom_new_user.exists())

    def test_003_write_user(self):
        with mock.patch('%s.update_user' % (self.path_zoom_api_v2), self._mock_request_update_user):
            self.user_zoom.write({'zoom_first_name': 'zoom_first_name_1'})
            self.assertEqual(self.user_zoom.zoom_first_name, 'zoom_first_name_1',
                             "to_zoom_calendar: error write zoom user")

    def test_004_write_user_fail(self):
        old_zoom_first_name = self.user_zoom.zoom_first_name
        with mock.patch('%s.update_user' % (self.path_zoom_api_v2), self._mock_request_update_user_fail):
            with self.assertRaises(ValidationError):
                self.user_zoom.write({'zoom_first_name': 'test_fail_88888'})
                self.assertEqual(self.user_zoom.zoom_first_name, old_zoom_first_name,
                                 "to_zoom_calendar: error write zoom user")

    def test_005_ulink_user(self):
        with mock.patch('%s.delete_user' % (self.path_zoom_api_v2), self._mock_request_delete_user):
            self.user_zoom.unlink()
            self.assertFalse(self.user_zoom.exists())

    def test_006_ulink_user_fail(self):
        with mock.patch('%s.delete_user' % (self.path_zoom_api_v2), self._mock_request_delete_user_fail):
            with self.assertRaises(ValidationError):
                self.user_zoom.unlink()
                self.assertTrue(self.user_zoom.exists())
