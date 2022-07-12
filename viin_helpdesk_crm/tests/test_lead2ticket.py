from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.viin_helpdesk.tests.test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install', 'external')
class TestLead2Ticket(TestHelpdeskCommon):

    @classmethod
    def setUpClass(cls):
        super(TestLead2Ticket, cls).setUpClass()
        cls.ticket_type = cls.env.ref('viin_helpdesk.helpdesk_ticket_type_question')

        cls.lead = cls.env.ref('crm.crm_case_1')
        cls.opportunity = cls.env.ref('crm.crm_case_13')

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_lead2ticket(self, mock_send_mail):
        mock_send_mail.return_value = True

        team_general = self.team_general

        # Check data
        self.assertEqual(True, self.lead.active, 'Lead is not active')
        self.assertEqual(0, self.lead.ticket_count, 'Lead has been links with ticket')

        # Test: lead2ticket
        lead2ticket = self.env['lead2ticket.wizard'].with_context(active_ids=[self.lead.id]).create({
            'ticket_type_id': self.ticket_type.id,
            'team_id': team_general.id,
            })
        lead2ticket.action_create_ticket()

        self.lead.invalidate_cache()  # to recompute ticket_count's value
        self.assertEqual(False, self.lead.active, 'Lead is active')
        self.assertEqual(1, self.lead.ticket_count, 'Lead has not been links with ticket')

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_lead2ticket_for_yourself(self, mock_send_mail):
        mock_send_mail.return_value = True

        team_general = self.team_general

        # Check data
        self.assertEqual(True, self.lead.active, 'Lead is not active')
        self.assertEqual(0, self.lead.ticket_count, 'Lead has been links with ticket')

        # Test: lead2ticket
        self.lead.user_id = self.user_member_user
        self.user_member_user.write({'groups_id': [(4, self.ref('sales_team.group_sale_salesman'))]})
        lead2ticket = self.env['lead2ticket.wizard'] \
                        .with_context(active_ids=[self.lead.id]) \
                        .with_user(self.user_member_user).create({
                            'ticket_type_id': self.ticket_type.id,
                            'team_id': team_general.id,
                            'assign_to_me': True,
                            })
        lead2ticket.action_create_ticket()

        self.assertEqual(False, self.lead.active, 'Lead is active')

        self.lead.invalidate_cache()  # to recompute ticket_count's value
        self.assertEqual(1, self.lead.ticket_count, 'Lead has not been links with ticket')
        self.assertRecordValues(self.lead.ticket_ids, [{
            'email_from': self.lead.email_from,
            'lead_id': self.lead.id,
            'user_id': self.user_member_user.id
        }])

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_lead2ticket_with_pretty_format_a_2_tuple(self, mock_send_mail):
        mock_send_mail.return_value = True

        team_general = self.team_general

        # Check data
        self.assertEqual(True, self.lead.active, 'Lead is not active')
        self.assertEqual(0, self.lead.ticket_count, 'Lead has been links with ticket')

        # Test: lead2ticket
        self.lead.write({
            'user_id': self.user_member_user.id,
            'email_from': '"User B - Company A" <user_a@company_a.com>',
            })
        self.user_member_user.write({'groups_id': [(4, self.ref('sales_team.group_sale_salesman'))]})
        lead2ticket = self.env['lead2ticket.wizard'] \
                        .with_context(active_ids=[self.lead.id]) \
                        .with_user(self.user_member_user).create({
                            'ticket_type_id': self.ticket_type.id,
                            'team_id': team_general.id,
                            'assign_to_me': True,
                            })
        lead2ticket.action_create_ticket()

        self.assertEqual(False, self.lead.active, 'Lead is active')

        self.lead.invalidate_cache()  # to recompute ticket_count's value
        self.assertEqual(1, self.lead.ticket_count, 'Lead has not been links with ticket')
        self.assertRecordValues(self.lead.ticket_ids, [{
            'email_from': 'user_a@company_a.com',
            'contact_name': 'User B - Company A',
            'lead_id': self.lead.id,
            'user_id': self.user_member_user.id
        }])

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_opp_create_ticket(self, mock_send_mail):
        mock_send_mail.return_value = True

        team_general = self.team_general

        # Check data
        self.assertEqual(True, self.opportunity.active, 'Opportunity is not active')
        self.assertEqual(0, self.opportunity.ticket_count, 'Opportunity has been links with ticket')

        # Test: lead2ticket
        lead2ticket = self.env['lead2ticket.wizard'].with_context(active_ids=[self.opportunity.id]).create({
            'ticket_type_id': self.ticket_type.id,
            'team_id': team_general.id,
            })
        lead2ticket.action_create_ticket()

        self.assertEqual(False, self.opportunity.active, 'Opportunity is active')

        self.opportunity.invalidate_cache()  # to recompute ticket_count's value
        self.assertEqual(1, self.opportunity.ticket_count, 'Opportunity has not been links with ticket')
