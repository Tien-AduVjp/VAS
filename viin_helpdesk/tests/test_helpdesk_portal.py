from lxml import html

from odoo.tests import HttpCase, tagged
from odoo.exceptions import AccessError
from odoo.tools import mute_logger

from .test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install', 'external')
class TestHelpdeskPortal(HttpCase):

    ticket_name = 'Table legs are unbalanced'

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_portals(self):
        # Test method _create_new_helpdesk ('/my/tickets/create' url)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        create_url = base_url + '/my/tickets/create'
        portal = self.env.ref('base.demo_user0')
        self.authenticate(portal.login, 'portal')

        # Get data form from '/my/tickets/create'
        res = self.opener.get(create_url)
        dom = html.fromstring(res.content)
        csrf_token = dom.xpath("//input[@name='csrf_token']")[0].value

        # Prepare ticket data
        data = {
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

        # Post to '/my/tickets/create'
        res = self.opener.post(create_url, data=data)

        # Find ticket matching ticket_name
        ticket = self.env['helpdesk.ticket'].search([('name', '=', self.ticket_name)], limit=1)

        self.assertEqual(ticket.partner_id, portal.partner_id, 'Create new ticket with portal user not ok')
        self.assertEqual(self.ticket_name, ticket.name, 'Create new ticket with portal user not ok')

        # Test method portal_my_ticket ('/my/tickets/<int:ticket_id>' url)
        ticket_url = base_url + '/my/tickets/%s' % ticket.id
        res = self.opener.get(ticket_url)

        self.assertEqual(200, res.status_code, 'Get ticket by id with portal user not ok')
        self.assertNotEqual(-1, str(res.content).find(self.ticket_name), 'Find ticket by name in response not ok')

        root = html.fromstring(res.content)
        # test view state
        status = root.xpath("//span[contains(@class, 'ticket-status')]")[0].text
        self.assertEqual(status, 'New')
        ticket.stage_id = self.env.ref('viin_helpdesk.helpdesk_stage_resolved').id
        ticket.flush(['stage_id'])
        res = self.url_open(ticket_url)
        root = html.fromstring(res.content)
        status = root.xpath("//span[contains(@class, 'ticket-status')]")[0].text
        self.assertEqual(status, 'Resolved')

        # View ticket is not exists
        ticket_url = base_url + '/my/tickets/%s?' % 9999999
        # response url is 'http://localhost:8069/my'

        url = self.opener.get(ticket_url, params={'access_token': 1}).url

        self.assertEqual(base_url + '/my', url, 'View ticket by id not ok')

        # Test method portal_my_tickets ('/my/tickets' url)
        ticket_url = base_url + '/my/tickets'
        res = self.opener.get(ticket_url)

        self.assertEqual(200, res.status_code, 'Get ticket by id with portal user not ok')
        self.assertNotEqual(-1, str(res.content).find(self.ticket_name), 'Find ticket by name in response not ok')

        # Test: read ticket with Employee
        self.assertRaises(AccessError, ticket.with_user(self.env.ref('base.user_demo')).read, ['id'])
