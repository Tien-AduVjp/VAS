from odoo.tools import mute_logger
from odoo.tests import tagged

from .test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install', 'external', 'access_rights')
class TestAddFollowers(TestHelpdeskCommon):

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_add_partner_to_followers_list(self):
        partner = self.user_employee_user.partner_id

        self.assertNotIn(partner, self.ticket_portal.message_partner_ids, 'Employee already in followers list!')

        vals = {
            'partner_ids': [partner.id],
            'channel_ids': [],
            'body': '<a href="%s/web#model=res.partner&amp;id=%s" class="o_mail_redirect" data-oe-id="%s" data-oe-model="res.partner" target="_blank">@%s</a> test' %
                (self.ticket_portal.get_base_url(), partner.id, partner.id, partner.name),
            'attachment_ids': [],
            'canned_response_ids': [],
            'message_type': 'comment',
            'subtype_xmlid': 'mail.mt_note'
        }
        self.ticket_portal.sudo().message_post(**vals)
        self.assertIn(partner, self.ticket_portal.message_partner_ids, 'Employee is not in followers list!')

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_add_channel_to_followers_list(self):
        channel = self.env.ref('mail.channel_all_employees')

        self.assertNotIn(channel, self.ticket_portal.message_channel_ids, 'Channel already in followers list!')

        vals = {
            'partner_ids': [],
            'channel_ids': [channel.id],
            'body': '<a href="%s/web#model=mail.channel&amp;id=%s" class="o_channel_redirect" data-oe-id="%s" data-oe-model="mail.channel" target="_blank">#%s</a> test' %
                (self.ticket_portal.get_base_url(), channel.id, channel.id, channel.name),
            'attachment_ids': [],
            'canned_response_ids': [],
            'message_type': 'comment',
            'subtype_xmlid': 'mail.mt_note'
        }
        self.ticket_portal.sudo().message_post(**vals)
        self.assertIn(channel, self.ticket_portal.message_channel_ids, 'Channel is not in followers list!')
