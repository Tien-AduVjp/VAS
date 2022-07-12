from odoo import fields
from odoo.tests.common import SingleTransactionCase
from odoo.tools import formataddr


class MobileNotificationCommon(SingleTransactionCase):

    def setUp(self, number_partner=4):
        super(MobileNotificationCommon, self).setUp()

        if number_partner < 4:
            number_partner = 4
        self.list_partner = self.env['res.partner']
        self.list_token = []
        self.list_token_obj = []
        self.device_tokens = self.env['mobile.device.token']
        self.user_1 = self.env.ref('base.user_demo')
        self.user_2 = self.env.ref('base.user_admin')

        self.channel_1 = self.env['mail.channel'].create({
            'name': 'channel_1'
        })
        for i in range(number_partner):
            if i == 0:
                partner = self.user_1.partner_id
            elif i == 1:
                partner = self.user_2.partner_id
            else:
                partner = self.env['res.partner'].create({
                    'name': 'viin_mobile_test_partner_{}'.format(i),
                    'email': 'partner_{}@example.com'.format(i)}
                )
            self.list_partner += partner

            token = self._token_vals('token_ios_{}'.format(i), platform='ios' if i % 2 == 0 else 'android')
            token_2 = self._token_vals('token_android_{}'.format(i), platform='android' if i % 2 == 0 else 'ios')

            self.list_token.append(token['token'])
            self.list_token_obj.append(token)
            self.device_tokens += self._create_device_token(partner, token)

            self.list_token.append(token_2['token'])
            self.list_token_obj.append(token_2)
            self.device_tokens += self._create_device_token(partner, token_2)

            self.channel_1.write({
                'channel_partner_ids': [(4, partner.id)]
            })

        self.channel_2 = self.env['mail.channel'].create({
            'name': 'channel_2',
            'channel_partner_ids': [
                (4, self.list_partner[0].id),
                (4, self.list_partner[1].id),
                (4, self.list_partner[2].id),
            ]
        })

    def set_up_mess_for_channel(self, channel, number_message, author, partner_1, partner_2):
        for i in range(number_message):
            notify = self._create_notify(partner_1, partner_2)
            message = self._create_new_message(
                res_id=channel.id,
                author=author,
                notify_id=notify.id
            )
            channel.write({
                'channel_message_ids': [(4, message.id)]
            })

    def set_up_notify_for_mail_thread(self, number_message, author, partner_1, partner_2, model=False):
        for i in range(number_message):
            notify = self._create_notify(partner_1, partner_2)
            message = self._create_new_message(
                model=model or 'res.partner',
                res_id=1,
                author=author,
                notify_id=notify.id
            )
            notify = self.env['mail.notification'].create({
                'mail_message_id': message.id,
                'res_partner_id': partner_1.id,
                'is_read': False,
                'notification_type': 'email',
            })
            return message

    def _create_notify(self, partner_1, partner_2, state_1=False, state_2=False):
        notification = self.env['mobile.notification'].create({
            'title': 'notification_1',
            'body': 'notification_1',
            'line_ids': [(0, 0, {
                'partner_id': partner_1.id,
                'state': state_1 or 'new',
                'retried_count': 0,
                'message_id': '',
                'error_message': '',
            }), (0, 0, {
                'partner_id': partner_2.id,
                'state': state_2 or 'new',
                'retried_count': 0,
                'message_id': '',
                'error_message': '',
            })]
        })
        return notification

    def setup_config(self):
        ConfigParams = self.env['ir.config_parameter'].sudo()
        ConfigParams.set_param('mobile.notify_provider', 'firebase')
        ConfigParams.set_param('mobile.notify_auth_key', 'test_auth_key')
        ConfigParams.set_param('mobile.notify_type', 'silent')
        ConfigParams.set_param('mobile.notify_max_retry', 5)
        ConfigParams.set_param('mobile.base_package', 'package_name')

    def _create_new_message(self, res_id, notify_id, author, status='pending_moderation', body='', model='mail.channel'):
        message = self.env['mail.message'].create({
            'model': model,
            'res_id': res_id,
            'mobile_notification_ids': [(6, 0, [notify_id])],
            'message_type': 'email',
            'body': body,
            'moderation_status': status,
            'author_id': author.id,
            'email_from': formataddr((author.name, author.email)),
        })
        return message

    def _create_device_token(self, parter, token):
        device_token = self.env['mobile.device.token'].create({
            'token': token['token'],
            'partner_id': parter.id,
            'platform': token['platform'],
            'package_name': token['package_name']
        })
        return device_token

    def _user_vals(self, user_name, partner):
        return {
            'name': user_name,
            'login': user_name,
            'email': user_name + '@example.com',
            'password': 'password',
            'partner_id': partner.id,
        }

    def _token_vals(self, token_name, platform=False):
        return {
            'token': 'viin_mobile_test_mode_' + token_name,
            'platform': platform or 'android',
            'package_name': 'package_name',
        }
