import logging
import requests
import json
from time import sleep
from concurrent.futures import ThreadPoolExecutor

from odoo import models, fields, api

executor_request = ThreadPoolExecutor(max_workers=5)
executor_update_database = ThreadPoolExecutor(max_workers=1)
_logger = logging.getLogger(__name__)

count_worker_request = 0
count_worker_update_database = 0


def get_count_worker_request():
    return count_worker_request


def get_count_worker_update_database():
    return count_worker_update_database


class MobileNotification(models.Model):
    _name = 'mobile.notification'
    _description = "Mobile Notification"
    _rec_name = 'title'

    title = fields.Char(string='Title', readonly=True)
    body = fields.Char(string='Body', readonly=True)
    data = fields.Text(string='Data')
    state = fields.Selection([
        ('new', 'New'),
        ('waiting', 'Waiting'),
        ('partially_success', 'Partially Success'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ], string='Status', default='new', required=True, compute='_compute_state')

    # TODO: rename notification_detail_ids to line_ids in master/14+
    notification_detail_ids = fields.One2many(
        'mobile.notification.detail', 'notification_id', string='Details')
    mail_message_id = fields.Many2one('mail.message', string='Mail message')
    group = fields.Char(string="Group", readonly=True)

    @api.depends('notification_detail_ids.state')
    def _compute_state(self):
        """
        Method used to compute state of notification
        If all notification detail state is cancelled, notification state will be failed
        If all notification detail state is success, notification state will be success
        If one notification detail state is failed, notification state will be waiting
        Else notification state will be partially_success
        """
        for r in self:
            number_success = 0
            number_cancelled = 0
            number_failed = 0
            for line in r.notification_detail_ids:
                if line.state == 'success':
                    number_success += 1
                elif line.state == 'cancelled':
                    number_cancelled += 1
                else:
                    number_failed += 1

            lines_count = len(r.notification_detail_ids)
            if number_failed > 0:
                r.state = 'waiting'
            elif number_success == lines_count:
                r.state = 'success'
            elif number_cancelled == lines_count:
                r.state = 'failed'
            else:
                r.state = 'partially_success'

    def _resend_notifications(self):
        # TODO: remove me in master/14+
        _logger.warning("The method `_resend_notifications()` is deprecated. Please call _resend() instead.")
        self._resend()

    @api.model
    def _resend(self):
        """
        Method used to resend notification has state new or waitting
        """
        notification_details = self.env['mobile.notification.detail'].sudo().search(
            [('state', 'in', ['new', 'failed'])])
        notifications = notification_details.sudo().mapped('notification_id')
        notifications._send(True)

    def _send(self, resend=False):
        """
        Method used to prepare data then call function _send_request of provider was selected
        Note when app was kill, ios platform only receive noisy push notification
        All notification from models that have not specified a mobile application will be sent to the base application
        @param {list} notification_details: list record notification detail
        """
        ConfigParams = self.env['ir.config_parameter'].sudo()
        mobile_notify_provider = ConfigParams.get_param('mobile.notify_provider', False)
        notify_type = ConfigParams.get_param('mobile.notify_type', '')
        mobile_base_package = ConfigParams.get_param('mobile.base_package', '')
        if mobile_notify_provider == False:
            return

        request_data_map = {}
        for r in self:
            if resend:
                notification_details = r.notification_detail_ids.filtered(lambda r: r.state in ('failed', 'new'))
            else:
                notification_details = r.notification_detail_ids
            record_device_tokens = notification_details.partner_id.sudo().mobile_token_ids
            device_tokens = record_device_tokens.filtered(lambda r: r.package_name == mobile_base_package)
            reg_data = {
                'list_tokens_silent': [],
                'list_tokens_noisy': [],
                'response_silent': False,
                'response_noisy': False,
                'request_url': False,
                'http_request_data': False,
                'resend': resend,
                'notification_details': notification_details,
                '_context': self._context,
            }
            if not device_tokens:
                if resend:
                    r._update_notification_detail(reg_data)
                continue

            list_tokens_silent = []
            list_tokens_noisy = []
            if notify_type == 'silent':
                for device_token in device_tokens:
                    if device_token.platform == 'android':
                        list_tokens_silent.append(device_token.token)
                    else:
                        list_tokens_noisy.append(device_token.token)
            else:
                list_tokens_noisy = record_device_tokens.mapped('token')

            reg_data.update({
                'list_tokens_silent': list_tokens_silent,
                'list_tokens_noisy': list_tokens_noisy,
            })
            func_prepare_request_data_name = '_prepare_%s_request_data' % mobile_notify_provider
            func_get_provider_url = '_get_%s_url' % mobile_notify_provider
            if hasattr(r, func_prepare_request_data_name):
                headers, data_request_silent, data_request_noisy = getattr(r, func_prepare_request_data_name)(list_tokens_silent, list_tokens_noisy)
                reg_data.update({
                    'request_url': getattr(r, func_get_provider_url)(),
                    'http_request_data': {
                        'headers': headers,
                        'data_request_silent': json.dumps(data_request_silent),
                        'data_request_noisy': json.dumps(data_request_noisy)
                    }
                })
                request_data_map[r] = reg_data
        for notification, data in request_data_map.items():
            global count_worker_request
            count_worker_request += 1
            future = executor_request.submit(notification.thread_pool_http_requests, data)
            future.add_done_callback(notification._update_notification_detail)

    def thread_pool_http_requests(self, data):
        self.ensure_one()
        with api.Environment.manage(), self.pool.cursor() as cr:
            try:
                env = self.env(cr=cr)
                notification_details = data['notification_details']
                notification_details = notification_details.with_env(env)
                list_tokens_silent = data['list_tokens_silent']
                list_tokens_noisy = data['list_tokens_noisy']
                # if not data['resend'] and not data['_context'].get('run_test', False):
                if not data['resend']:
                    sleep(5)
                    message = self.with_env(env).mail_message_id
                    if message.model == 'mail.channel':
                        channel = message.channel_ids[0]
                        for channel_partner in channel.channel_last_seen_partner_ids:
                            if channel_partner.seen_message_id.id >= message.id:
                                notification_detail = notification_details.filtered(lambda r: r.partner_id.id == channel_partner.partner_id.id)
                                notification_detail.write({
                                    'state': 'success'
                                })
                                list_token_remove = notification_detail.partner_id.sudo().mobile_token_ids.mapped('token')
                                # Need to keep the correct index
                                notification_details -= notification_detail
                                for token_remove in list_token_remove:
                                    if token_remove in list_tokens_silent:
                                        list_tokens_silent.remove(token_remove)
                                    if token_remove in list_tokens_noisy:
                                        list_tokens_noisy.remove(token_remove)
                    data.update({
                        'notification_details': notification_details,
                        'list_tokens_silent': list_tokens_silent,
                        'list_tokens_noisy': list_tokens_noisy,
                    })
                return self.with_env(env).do_http_requests(data)
            except Exception as e:
                _logger.error("Mobile Notification Error: %s", str(e))

    def do_http_requests(self, data):
        self.ensure_one()
        http_request_data = data['http_request_data']

        if data['list_tokens_silent']:
            try:
                data['response_silent'] = requests.post(
                    data['request_url'],
                    headers=http_request_data['headers'],
                    data=http_request_data['data_request_silent'],
                    timeout=3,
                )
            except:
                data['response_silent'] = False
        if data['list_tokens_noisy']:
            try:
                data['response_noisy'] = requests.post(
                    data['request_url'],
                    headers=http_request_data['headers'],
                    data=http_request_data['data_request_noisy'],
                    timeout=3,
                )
            except:
                data['response_noisy'] = False
        return data

    def _update_notification_detail(self, data):
        self.ensure_one()
        if not type(data) == dict:
            data = data._result
        global count_worker_request, count_worker_update_database
        count_worker_request -= 1
        count_worker_update_database += 1
        future = executor_update_database.submit(self.thread_pool_update_detail, data)
        future.add_done_callback(self.done_update_database)

    def done_update_database(self, data):
        global count_worker_update_database
        count_worker_update_database -= 1

    def thread_pool_update_detail(self, data):
        with api.Environment.manage(), self.pool.cursor() as cr:
            try:
                env = self.env(cr=cr)
                notification_details = data['notification_details']
                notification_details = notification_details.with_env(env)
                data.update({
                    'notification_details': notification_details
                })
                mobile_notify_provider = self.env['ir.config_parameter'].with_env(env).sudo().get_param('mobile.notify_provider', False)
                func_response_validation = '_validate_%s_response' % mobile_notify_provider
                if hasattr(self.with_env(env), func_response_validation):
                    getattr(self.with_env(env), func_response_validation)(data)
            except Exception as e:
                _logger.error("Mobile Notification Error: %s", str(e))

    def _cancel(self, groups=False, notify_ids=False):
        """
        Method used to call function _cancel of provider was selected
        @param {list} groups: list group of notifications
        @param {list} ids: list id of mail.notification marked as read
        """
        self.ensure_one()
        mobile_notify_provider = self.env['ir.config_parameter'].sudo().get_param('mobile.notify_provider', False)
        if mobile_notify_provider == False:
            return False
        notification_details = self.notification_detail_ids.filtered(lambda r: r.partner_id.id == self.env.user.partner_id.id)
        record_device_tokens = notification_details.partner_id.sudo().mobile_token_ids
        if record_device_tokens:
            list_token = record_device_tokens.mapped('token')
            function = getattr(self, '_cancel_notification_{}'.format(mobile_notify_provider))
            return function(list_token, groups, notify_ids)
        else:
            return False
