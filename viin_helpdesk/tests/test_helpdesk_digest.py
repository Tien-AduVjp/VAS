from odoo.tests import tagged
from .test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install')
class TestHelpdeskDigest(TestHelpdeskCommon):

    def _unlink_exist_ticket_record(self):
        self.env['helpdesk.ticket'].with_context(active_test=False).search([]).unlink()
        self._prepare_digest_ticket_data()

    def test_ticket_closed(self):
        self._unlink_exist_ticket_record()
        if self.digest_record.kpi_helpdesk_ticket_closed:
            helpdesk_ticket_close_yesterday = self.val_dict['yesterday']['kpi_helpdesk_ticket_closed']['kpi_helpdesk_ticket_closed']
            helpdesk_ticket_close_lastweek = self.val_dict['lastweek']['kpi_helpdesk_ticket_closed']['kpi_helpdesk_ticket_closed']
            helpdesk_ticket_close_lastmonth = self.val_dict['lastmonth']['kpi_helpdesk_ticket_closed']['kpi_helpdesk_ticket_closed']
            self.assertEqual(helpdesk_ticket_close_yesterday, 2, 'Test not OK')
            self.assertEqual(helpdesk_ticket_close_lastweek, 4, 'Test not OK')
            self.assertEqual(helpdesk_ticket_close_lastmonth, 6, 'Test not OK')

    def test_ticket_opened(self):
        self._unlink_exist_ticket_record()
        if self.digest_record.kpi_helpdesk_ticket_opened:
            helpdesk_ticket_open_yesterday = self.val_dict['yesterday']['kpi_helpdesk_ticket_opened']['kpi_helpdesk_ticket_opened']
            helpdesk_ticket_open_lastweek = self.val_dict['lastweek']['kpi_helpdesk_ticket_opened']['kpi_helpdesk_ticket_opened']
            helpdesk_ticket_open_lastmonth = self.val_dict['lastmonth']['kpi_helpdesk_ticket_opened']['kpi_helpdesk_ticket_opened']
            self.assertEqual(helpdesk_ticket_open_yesterday, 2, 'Test not OK')
            self.assertEqual(helpdesk_ticket_open_lastweek, 4, 'Test not OK')
            self.assertEqual(helpdesk_ticket_open_lastmonth, 6, 'Test not OK')
