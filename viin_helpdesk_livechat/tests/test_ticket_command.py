from odoo.tests import tagged, TransactionCase
from odoo.tools import html2plaintext


@tagged('post_install', '-at_install')
class TestTicketCommand(TransactionCase):

    def test_create_ticket_by_command(self):
        """ Test that when entering "/ticket your_ticket_name" in a discussion channel, a new ticket will be created
            with description description as conversation content """
        general_channel = self.env['mail.channel'].create({
            'name': 'channel test',
            'description': 'channel test',
            'group_ids': [(4, self.env.ref('base.group_user').id)]
        })
        kwargs = {
            'body': '/ticket TicketLiveChatTest',
            'message_type': 'comment',
            'subtype_xmlid': 'mail.mt_comment'
        }
        general_channel.with_user(self.env.ref('base.user_admin')).message_post(body='Message 01',
                                                                                message_type='comment',
                                                                                subtype_xmlid='mail.mt_comment')
        general_channel.with_user(self.env.ref('base.user_demo')).message_post(body='Message 02',
                                                                               message_type='comment',
                                                                               subtype_xmlid='mail.mt_comment')
        general_channel.with_user(self.env.ref('base.user_demo')).execute_command(command='ticket', **kwargs)
        ticket = self.env['helpdesk.ticket'].search([('name', '=', 'TicketLiveChatTest')])
        ticket_description = html2plaintext(''.join(
            '<b>%s</b>: %s<br/>' % (message.author_id.name, message.body)
            for message in general_channel.channel_message_ids.sorted('id')))
        self.assertEqual(ticket_description, html2plaintext(ticket.description))
        self.assertEqual(ticket.partner_id, self.env.ref('base.partner_root'))
