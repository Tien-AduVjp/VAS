from odoo import fields
from odoo.tests.common import SingleTransactionCase
from odoo.tools import formataddr


class MobileNotificationCommon(SingleTransactionCase):

    def setUp(self, number_partner=4):
        super(MobileNotificationCommon, self).setUp()

        if number_partner < 4:
            number_partner = 4
        res_user = self.env['res.users']
        ResPartner = self.env['res.partner']
        self.MailChannelPartner = self.env['mail.channel.partner']
        self.MailChannel = self.env['mail.channel']
        self.MobileNotification = self.env['mobile.notification']
        self.MobileDeviceToken = self.env['mobile.device.token']
        self.list_partner = []
        self.list_token = []
        self.list_token_obj = []
        self.user_1 = self.env.ref('base.user_demo')
        # reset message
        self.env['mail.channel.partner'].search([('partner_id', '=', self.user_1.partner_id.id)]).unlink()

        self.channel_1 = self.MailChannel.create({
            'name': 'channel_1'
        })
        for i in range(number_partner):
            if i == 0:
                partner = self.user_1.partner_id
            else:
                partner = ResPartner.create({
                    'name': 'viin_mobile_test_partner_{}'.format(i),
                    'email': 'partner_{}@example.com'.format(i)}
                )
            self.list_partner.append(partner)

            token = self._token_vals('token_{}'.format(i), platform='ios' if i % 2 == 0 else 'android')
            token_2 = self._token_vals('token_{}'.format(i), platform='android' if i % 2 == 0 else 'ios')

            self.list_token.append(token['token'])
            self.list_token_obj.append(token)
            self._create_device_token(partner, token)

            self.list_token.append(token_2['token'])
            self.list_token_obj.append(token_2)
            self._create_device_token(partner, token_2)

            self.channel_1.write({
                'channel_partner_ids': [(4, partner.id)]
            })

        self.channel_2 = self.MailChannel.create({
            'name': 'channel_2',
            'channel_partner_ids': [
                (4, self.list_partner[0].id),
                (4, self.list_partner[1].id),
                (4, self.list_partner[2].id),
            ]
        })
        # partner_id 1, 2 for user admin and demo
        self.MailChannelPartner.search([('partner_id', '=', 1), ('channel_id', '=', self.channel_1.id)]).unlink()
        self.MailChannelPartner.search([('partner_id', '=', 2), ('channel_id', '=', self.channel_1.id)]).unlink()
        self.MailChannelPartner.search([('partner_id', '=', 1), ('channel_id', '=', self.channel_2.id)]).unlink()
        self.MailChannelPartner.search([('partner_id', '=', 2), ('channel_id', '=', self.channel_2.id)]).unlink()

    def set_up_mess_for_channel(self, channel, number_message, author, partner_1, partner_2):
        for i in range(number_message):
            notify = self._create_notify('group_channel_1', partner_1, partner_2)
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
            notify = self._create_notify('group_3', partner_1, partner_2)
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

    def _create_notify(self, group, partner_1, partner_2, data=False, state_1=False, state_2=False):
        notification = self.MobileNotification.create({
            'title': 'notification_1',
            'body': 'notification_1',
            'data': data or {'action': 99, 'res_model': 'mail.channel', 'active_id': 12},
            'group': group,
            'notification_detail_ids': [(0, 0, {
                'partner_id': partner_1.id,
                'state': state_1 or 'new',
                'retried_count': 0,
                'send_date': fields.datetime.now(),
                'message_id': '',
                'error_message': '',
            }), (0, 0, {
                'partner_id': partner_2.id,
                'state': state_2 or 'new',
                'retried_count': 0,
                'send_date': fields.datetime.now(),
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
            'mobile_notification_id': notify_id,
            'message_type': 'email',
            'body': body,
            'moderation_status': status,
            'author_id': author.id,
            'email_from': formataddr((author.name, author.email)),
        })
        return message

    def _create_device_token(self, parter, token):
        device_token = self.MobileDeviceToken.create({
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
