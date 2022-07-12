from lxml import html

from odoo.tests import HttpCase, tagged
from odoo.tools import mute_logger
from odoo.addons.viin_helpdesk.tests.test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install', 'external')
class TestHelpdeskPortal(TestHelpdeskCommon, HttpCase):
    
    def setUp(self):
        super(TestHelpdeskPortal, self).setUp()
        
        self.ticket_name = 'Table legs are unbalanced'
        
        self.portal = self.env.ref('base.demo_user0')
        self.patch(type(self.env['res.users']), '_login', lambda db, login, password: self.portal.id)
    
    @mute_logger('odoo.addons.base.models.ir_model')
    def test_portals(self):
        # Test method _create_new_helpdesk ('/my/tickets/create' url)
        
        team_general = self.team_general
        
        sale_order = self.env['sale.order'].create({
            'partner_id': self.portal.partner_id.id,
            'partner_invoice_id': self.portal.partner_id.id,
            'partner_shipping_id': self.portal.partner_id.id,
        })
        
        base_url = team_general.get_base_url()
        create_url = base_url + '/my/tickets/create?saleorder=%s' % sale_order.id
        
        self.authenticate(self.portal.login, 'portal')
        
        # Get data form from '/my/tickets/create?saleorder=%s'
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
        
        # Post to '/my/tickets/create?saleorder=%s'
        res = self.opener.post(create_url, data=data)
        
        # Find ticket matching ticket_name
        ticket = self.env['helpdesk.ticket'].search([('name', '=', self.ticket_name)], limit=1)
        
        self.assertEqual(ticket.partner_id, self.portal.partner_id, 'Create new ticket with portal user not ok')
        self.assertEqual(self.ticket_name, ticket.name, 'Create new ticket with portal user not ok')
        self.assertEqual(sale_order.id, ticket.sale_order_id.id, 'Ticket has not been link with sale order')
