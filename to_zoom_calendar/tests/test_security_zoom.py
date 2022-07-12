from unittest import mock
from odoo.exceptions import AccessError

from odoo.tests.common import tagged
from .common import ZoomCommon


@tagged('post_install', '-at_install')
class TestZoomSecurity(ZoomCommon):
    def test_01_no_group(self):
        """ user_demo hase no group of Zoom calendar
            user_demo can't do anything Zoom user"""
        self.assertRaises(AccessError,
                          self.user_zoom.with_user(self.user_demo).read, ['id'])
        with mock.patch('%s.update_user' % (self.path_zoom_api_v2), self._mock_request_update_user):
            self.assertRaises(AccessError,
                              self.user_zoom.with_user(self.user_demo).write,
                              {'zoom_first_name': 'zoom_first_name_1'})
        with mock.patch('%s.delete_user' % (self.path_zoom_api_v2), self._mock_request_delete_user):
            self.assertRaises(AccessError,
                              self.user_zoom.with_user(self.user_demo).unlink)
        with mock.patch('%s.create_user' % (self.path_zoom_api_v2), self._mock_request_create_user):
            self.assertRaises(AccessError,
                              self.env['zoom.user'].with_user(self.user_demo).create,
                              self._vals_create_zoom_user('test_1'))

    def test_02_group_user(self):
        """ user_demo has group group_user of Zoom calendar
            user_demo can only read Zoom user"""
        group_user = self.env.ref('to_zoom_calendar.group_user').id
        self.user_demo.write({'groups_id': [(6, 0, [group_user])]})

        self.user_zoom.with_user(self.user_demo).read(['id'])
        with mock.patch('%s.update_user' % (self.path_zoom_api_v2), self._mock_request_update_user):
            self.assertRaises(AccessError,
                              self.user_zoom.with_user(self.user_demo).write,
                              {'zoom_first_name': 'zoom_first_name_1'})
        with mock.patch('%s.delete_user' % (self.path_zoom_api_v2), self._mock_request_delete_user):
            self.assertRaises(AccessError,
                              self.user_zoom.with_user(self.user_demo).unlink)

        with mock.patch('%s.create_user' % (self.path_zoom_api_v2), self._mock_request_create_user):
            self.assertRaises(AccessError,
                              self.env['zoom.user'].with_user(self.user_demo).create,
                              self._vals_create_zoom_user('test_2'))

    def test_03_group_admin(self):
        """ user_demo has group group_admin of Zoom calendar
            user_demo can do anything Zoom user"""
        group_admin = self.env.ref('to_zoom_calendar.group_admin').id
        self.user_demo.write({'groups_id': [(6, 0, [group_admin])]})

        self.user_zoom.with_user(self.user_demo).read(['id'])

        with mock.patch('%s.update_user' % (self.path_zoom_api_v2), self._mock_request_update_user):
            self.user_zoom.with_user(self.user_demo).write({'zoom_first_name': 'zoom_first_name_1'})

        with mock.patch('%s.delete_user' % (self.path_zoom_api_v2), self._mock_request_delete_user):
            self.user_zoom.with_user(self.user_demo).unlink()

        with mock.patch('%s.create_user' % (self.path_zoom_api_v2), self._mock_request_create_user):
            self.env['zoom.user'].with_user(self.user_demo).create(self._vals_create_zoom_user('test_3'))
