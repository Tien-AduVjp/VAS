from lxml import html

from odoo.tests import HttpCase, tagged
from odoo.tools import mute_logger

from odoo.addons.viin_helpdesk.tests.test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestWebsiteHelpdesk(HttpCase, TestHelpdeskCommon):

    def setUp(self):
        super(TestWebsiteHelpdesk, self).setUp()

        self.ticket_name = 'Table legs are unbalanced'

        # perform no mail features for better perfomance
        def _send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None, notif_layout=False):
            return self.env['mail.mail']

        self.patch(type(self.env['mail.template']), 'send_mail', _send_mail)

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_create_new_ticket(self):

        # Test method _create_new_helpdesk ('/ticket/create' url)
        team_general = self.team_general
        team_general.write({'website_published': True})
        team_general.flush(['website_published'])

        base_url = team_general.get_base_url()
        create_url = base_url + '/ticket/create'

        # Get data form from '/ticket/create'
        res = self.opener.get(create_url)
        dom = html.fromstring(res.content)
        csrf_token = dom.xpath("//input[@name='csrf_token']")[0].value

        # Prepare ticket data
        contact_name = 'Public User'
        email_from = 'public@example.viindoo.com'
        data = {
            'contact_name': contact_name,
            'email_from': email_from,
            'name': self.ticket_name,
            'description': """
Hi,

A few days ago, I bought a Four Persons Desk. While assembling it in my office, I found that the legs of the table were not properly balanced. Could you please come and fix this?

Kindly do this as early as possible.

Best,
Azure Interior
            """,
            'csrf_token': csrf_token,
        }

        # Post to '/ticket/create'
        # Captcha is validated
        res = self.opener.post(create_url, data=data)

        ticket = self.env['helpdesk.ticket'].search([('name', '=', self.ticket_name)], limit=1)

        self.assertEqual(contact_name, ticket.contact_name, 'Create new ticket with public user not ok')
        self.assertEqual(email_from, ticket.email_from, 'Create new ticket with public user not ok')
