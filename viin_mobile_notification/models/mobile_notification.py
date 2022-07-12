import logging
import threading
import requests
import json

from concurrent.futures import ThreadPoolExecutor
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.addons.to_base.models.to_base import after_commit

executor_update_database = ThreadPoolExecutor(max_workers=1)
executor_cancel_notification = ThreadPoolExecutor(max_workers=1)
_logger = logging.getLogger(__name__)


class MobileNotification(models.Model):
    _name = 'mobile.notification'
    _description = "Mobile Notification"
    _rec_name = 'title'

    title = fields.Char(string='Title', readonly=True)
    body = fields.Char(string='Body', readonly=True)
    # TODO: master/15+, remove field data.
    data = fields.Text(string='Data')
    state = fields.Selection([
        ('new', 'New'),
        ('waiting', 'Waiting'),
        ('partially_success', 'Partially Success'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ], string='Status', compute='_compute_state')

    line_ids = fields.One2many('mobile.notification.detail', 'notification_id', string='Notification Partner')
    mail_message_id = fields.Many2one('mail.message', string='Mail message', ondelete='cascade', index=True)
    # TODO: master/15+, remove field group.
    group = fields.Char(string="Group", readonly=True, help="Used as a key so that mobile can collapse notifications")

    def _get_group_notification(self):
        """ Used as a key so that mobile can collapse notifications or cancel notification of channel """
        groups = []
        for r in self:
            group = '{%s}, {%s}' %(r.mail_message_id.model, r.mail_message_id.res_id)
            if group not in groups:
                groups.append(group)
        return groups

    def _prepare_data_to_open_in_view_window(self):
        """ To open in the view window on mobile apps """
        self.ensure_one()
        vals = {
            'res_model': self.mail_message_id.model,
        }
        if self.mail_message_id.model == 'mail.channel':
            vals.update({
                'action': self.env.ref('mail.action_discuss').id,
                'active_id': self.mail_message_id.res_id,
            })
        else:
            vals.update({
                'res_id': self.mail_message_id.res_id
            })
        return vals

    @api.depends('line_ids.state')
    def _compute_state(self):
        """
        Method used to compute state of notification
        If all notification lines's state is cancelled, notification's state will be failed
        If all notification lines's state is success, notification's state will be success
        If one notification line's state is failed, notification's state will be waiting
        Else notification's state will be partially_success
        """
        for r in self:
            number_success = 0
            number_cancelled = 0
            number_failed = 0
            for line in r.line_ids:
                if line.state == 'success':
                    number_success += 1
                elif line.state == 'cancelled':
                    number_cancelled += 1
                else:
                    number_failed += 1

            lines_count = len(r.line_ids)
            if number_failed > 0:
                r.state = 'waiting'
            elif number_success == lines_count:
                r.state = 'success'
            elif number_cancelled == lines_count:
                r.state = 'failed'
            else:
                r.state = 'partially_success'

    @api.model
    def _resend(self):
        """
        Method used to resend mobile.notification.detail has state new or failed
        The cause of the failed sending could be an unstable network connection, the system will try to resend these messages until it is marked as cancelled.
        """
        notification_lines = self.env['mobile.notification.detail'].sudo().search([('state', 'in', ('new', 'failed'))])
        notifications = notification_lines.sudo().mapped('notification_id')
        if notifications:
            notifications._send(True)

    def _send(self, resend=False):
        """
        Method used to prepare data then call function _send_request of provider was selected
        Note when app was kill, ios platform only receive noisy push notification
        All notification from models that have not specified a mobile application will be sent to the base application
        """
        ConfigParams = self.env['ir.config_parameter'].sudo()
        mobile_notify_provider = ConfigParams.get_param('mobile.notify_provider', False)
        if not mobile_notify_provider:
            return

        notify_type = ConfigParams.get_param('mobile.notify_type', '')
        mobile_pacakage = ConfigParams.get_param('mobile.base_package', '')
        responses = {}
        for r in self:
            req_data = r._prepare_req_data(mobile_pacakage, notify_type, resend)
            responses[r] = req_data
            if len(req_data['list_tokens_silent'])==0 and len(req_data['list_tokens_noisy'])==0:
                continue
            func_prepare_request_data_name = '_prepare_%s_request_data' % mobile_notify_provider
            func_get_provider_url = '_get_%s_url' % mobile_notify_provider
            if hasattr(r, func_prepare_request_data_name):
                headers, data_request_silent, data_request_noisy = getattr(r, func_prepare_request_data_name)(
                    req_data['list_tokens_silent'],
                    req_data['list_tokens_noisy']
                    )
                req_data.update({
                    'request_url': getattr(r, func_get_provider_url)(),
                    'http_request_data': {
                        'headers': headers,
                        'data_request_silent': json.dumps(data_request_silent),
                        'data_request_noisy': json.dumps(data_request_noisy)
                    }
                })
                responses[r] = r.do_http_requests(req_data)
        self._update_notification_detail(responses)
        if getattr(threading.main_thread(), 'testing', False) or self.env.registry.in_test_mode():
            self.env.cr.commit()

    def _prepare_req_data(self, mobile_pacakage, notify_type, resend):
        # Other modules can inherit this function then filter tokens to send notifications to different applications
        # Exam: message only need notification from mail.channel:
        # if self.mail_message_id.model == 'mail.channel':
        #       mobile_pacakage = 'com.message'
        # return self.super(Exam, self)._prepare_req_data(mobile_pacakage, notify_type, resend)
        self.ensure_one()
        if resend:
            notification_lines = self.line_ids.filtered(lambda l: l.state in ('failed', 'new'))
        else:
            notification_lines = self.line_ids
        record_device_tokens = notification_lines.partner_id.sudo().mobile_token_ids
        device_tokens = record_device_tokens.filtered(lambda t: t.package_name == mobile_pacakage)
        req_data = {
                'list_tokens_silent': [],
                'list_tokens_noisy': [],
                'response_silent': False,
                'response_noisy': False,
                'request_url': False,
                'http_request_data': False,
                'resend': resend,
                'notification_lines': notification_lines,
                '_context': self._context,
            }
        if device_tokens:
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
            req_data.update({
                'list_tokens_silent': list_tokens_silent,
                'list_tokens_noisy': list_tokens_noisy,
                })
        return req_data

    @api.model
    def do_http_requests(self, req_params):
        http_request_data = req_params['http_request_data']

        if req_params['list_tokens_silent']:
            try:
                req_params['response_silent'] = requests.post(
                    req_params['request_url'],
                    headers=http_request_data['headers'],
                    data=http_request_data['data_request_silent'],
                    timeout=3,
                    )
            except:
                req_params['response_silent'] = False
        if req_params['list_tokens_noisy']:
            try:
                req_params['response_noisy'] = requests.post(
                    req_params['request_url'],
                    headers=http_request_data['headers'],
                    data=http_request_data['data_request_noisy'],
                    timeout=3,
                    )
            except:
                req_params['response_noisy'] = False
        return req_params

    @after_commit
    def _update_notification_detail(self, responses):
        # After_commit decorator is required to sure thread was commit notification
        test_mode = getattr(threading.main_thread(), 'testing', False) or self.env.registry.in_test_mode()
        if test_mode:
            with ThreadPoolExecutor(max_workers=1) as ex:
                [ex.submit(r.thread_pool_update_detail, responses[r]) for r in self]
        else:
            for r in self:
                executor_update_database.submit(r.thread_pool_update_detail, responses[r])

    def thread_pool_update_detail(self, data):
        with api.Environment.manage(), self.pool.cursor() as cr:
            try:
                env = self.env(cr=cr)
                notification_lines = data['notification_lines']
                notification_lines = notification_lines.with_env(env)
                data.update({
                    'notification_lines': notification_lines
                })
                mobile_notify_provider = self.env['ir.config_parameter'].with_env(env).sudo().get_param('mobile.notify_provider', False)
                func_response_validation = '_validate_%s_response' % mobile_notify_provider
                if hasattr(self.with_env(env), func_response_validation):
                    getattr(self.with_env(env), func_response_validation)(data)
                    if getattr(threading.main_thread(), 'testing', False) or self.env.registry.in_test_mode():
                        env.cr.commit()
            except Exception as e:
                _logger.error("Mobile Notification Update Detail Error: %s", str(e))

    def _cancel(self, groups=False, notification_ids=False):
        """
        Method used to call function _cancel of provider was selected
        @param {list} groups: list group of notifications
        @param {list} ids: list id of mail.notification marked as read
        """
        self.ensure_one()
        mobile_notify_provider = self.env['ir.config_parameter'].sudo().get_param('mobile.notify_provider', False)
        if mobile_notify_provider == False:
            return False
        notification_lines = self.line_ids.filtered(lambda r: r.partner_id.id == self.env.user.partner_id.id)
        record_device_tokens = notification_lines.partner_id.sudo().mobile_token_ids
        if record_device_tokens:
            list_token = record_device_tokens.mapped('token')
            ConfigParams = self.env['ir.config_parameter'].sudo()
            key = ConfigParams.get_param('mobile.notify_auth_key', '')
            notify_type = ConfigParams.get_param('mobile.notify_type', '')
            if not key or not list_token:
                return False
            function = getattr(self, '_cancel_notification_{}'.format(mobile_notify_provider))

            test_mode = getattr(threading.main_thread(), 'testing', False) or self.env.registry.in_test_mode()
            groups = groups or self._get_group_notification()
            if test_mode:
                with ThreadPoolExecutor(max_workers=1) as ex:
                    ex.submit(function, list_token, key, notify_type, groups, notification_ids)
            else:
                executor_cancel_notification.submit(function, self.title, list_token, key, notify_type, groups, notification_ids)

    def _gc_mobile_notifications(self, max_age_days=7):
        notifications = self.search([('create_date', '<', fields.Datetime.now() - relativedelta(days=max_age_days))])
        # database with large number of users may generate hundred thousand records every days
        # deleting such all those in one call causes bad performance due to entire-recordset-prefetch-effects
        # Hence, we split in pieces of 1000 records then delete each
        for smaller_batch in self.env['to.base'].splittor(notifications):
            smaller_batch.unlink()
        return True
