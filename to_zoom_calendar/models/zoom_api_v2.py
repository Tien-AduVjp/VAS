import jwt
import requests
from odoo import models, fields
from odoo.exceptions import ValidationError

ZOOM_API_URL = 'https://api.zoom.us/v2/'


class ZoomAPIv2(models.AbstractModel):
    _name = 'zoom.apiv2'
    _description = 'Zoom API v2'

    def generate_JWT_key(self):
        """This method to generate JWT"""
        zoom_api_key = self.env.company.zoom_api_key
        zoom_secret_key = self.env.company.zoom_secret_key

        if not zoom_api_key or not zoom_secret_key:
            raise ValidationError('Please Configure Zoom Credentials')

        return jwt.encode({
            'iss': zoom_api_key,
            'exp': int(fields.Datetime.now().timestamp()) + 60
            }, zoom_secret_key, algorithm='HS256')

    def send_request(self, url_segment, data={}, method='GET'):
        """This method to send request to Zoom API"""
        url = ZOOM_API_URL + url_segment
        headers = {
            'Authorization': 'Bearer ' + self.generate_JWT_key(),
            'Content-Type': 'application/json',
            }
        res = False
        if method == 'GET':
            res = requests.get(url, headers=headers)
        elif method == 'DELETE':
            res = requests.delete(url, headers=headers)
        elif method == 'PATCH':
            res = requests.patch(url, json=data, headers=headers)
        elif method == 'PUT':
            res = requests.put(url, json=data, headers=headers)
        elif method == 'POST':
            res = requests.post(url, json=data, headers=headers)
        else:
            return False
        return res

    def get_meeting(self, meeting_id):
        """This method to get Zoom Meeting"""
        url_segment = 'meetings/%s' % meeting_id
        res = self.send_request(url_segment, method='GET')
        return res

    def get_meetings(self, user_id, page_size=30, page_number=1):
        """List all the meetings that were scheduled for a user (meeting host)."""
        url_segment = '/users/%s/meetings?type=scheduled&page_size=%s&page_number=%s' % (user_id, page_size, page_number)
        res = self.send_request(url_segment, method='GET')
        return res

    def create_meeting(self, user_id, data):
        """This method to generate Zoom Meeting"""
        res = self.send_request('users/%s/meetings' % user_id, data=data, method='POST')
        return res

    def update_meeting(self, meeting_id, data):
        """This method to update Zoom Meeting"""
        url_segment = 'meetings/%s' % meeting_id
        res = self.send_request(url_segment, data=data, method='PATCH')
        return res

    def delete_meeting(self, meeting_id):
        """This method to delete Zoom Meeting"""
        url_segment = 'meetings/%s' % meeting_id
        res = self.send_request(url_segment, method='DELETE')
        return res

    def get_user(self, user_id):
        """This method to get Zoom User"""
        url_segment = 'users/%s' % user_id
        res = self.send_request(url_segment, method='GET')
        return res

    def create_user(self, data):
        """A Zoom account can have one or more users. Use this method to add a new user to your account."""
        res = self.send_request('users', data=data, method='POST')
        return res

    def update_user(self, user_id, data):
        """Update information on a user’s Zoom profile."""
        url_segment = 'users/%s' % user_id
        res = self.send_request(url_segment, data=data, method='PATCH')
        return res

    def delete_user(self, user_id):
        """Update information on a user’s Zoom profile."""
        url_segment = 'users/%s' % user_id
        res = self.send_request(url_segment, method='DELETE')
        return res

    def get_report_users(self, date_from, date_to, page_size=30, page_number=1):
        """List number of meetings, number of meeting minutes for a specific time range, up to one month."""
        url_segment = '/report/users?type=active&from=%s&to=%s&page_size=%s&page_number=%s' % (date_from, date_to, page_size, page_number)
        res = self.send_request(url_segment, method='GET')
        return res
