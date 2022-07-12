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
            kpi_val = [kpi for kpi in self.kpis_data if kpi['kpi_name'] == 'kpi_helpdesk_ticket_closed'][0]
            helpdesk_ticket_close_yesterday = kpi_val['kpi_col1']['value']
            helpdesk_ticket_close_lastweek = kpi_val['kpi_col2']['value']
            helpdesk_ticket_close_lastmonth = kpi_val['kpi_col3']['value']
            self.assertEqual(helpdesk_ticket_close_yesterday, 2, 'Test not OK')
            self.assertEqual(helpdesk_ticket_close_lastweek, 4, 'Test not OK')
            self.assertEqual(helpdesk_ticket_close_lastmonth, 6, 'Test not OK')

    def test_ticket_opened(self):
        self._unlink_exist_ticket_record()
        if self.digest_record.kpi_helpdesk_ticket_opened:
            kpi_val = [kpi for kpi in self.kpis_data if kpi['kpi_name'] == 'kpi_helpdesk_ticket_opened'][0]
            helpdesk_ticket_open_yesterday = kpi_val['kpi_col1']['value']
            helpdesk_ticket_open_lastweek = kpi_val['kpi_col2']['value']
            helpdesk_ticket_open_lastmonth = kpi_val['kpi_col3']['value']
            self.assertEqual(helpdesk_ticket_open_yesterday, 2, 'Test not OK')
            self.assertEqual(helpdesk_ticket_open_lastweek, 4, 'Test not OK')
            self.assertEqual(helpdesk_ticket_open_lastmonth, 6, 'Test not OK')
