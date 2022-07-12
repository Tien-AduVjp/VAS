from datetime import date, datetime

from odoo.tests import TransactionCase


class TestCrmLead(TransactionCase):
    def setUp(self):
        super(TestCrmLead, self).setUp()

        self.crm_lead = self.env['crm.lead'].create({
            'name': 'Lead Test'
        })

    def test_compute_days_exceeding_closing(self):
        self.crm_lead.date_deadline = date(2021, 10, 8)
        self.crm_lead.date_closed = False
        self.assertFalse(self.crm_lead.days_exceeding_closing)

        self.crm_lead.date_deadline = False
        self.crm_lead.date_closed = datetime(2021, 9, 8)
        self.assertFalse(self.crm_lead.days_exceeding_closing)

        self.crm_lead.date_deadline = date(2021, 10, 8)
        self.crm_lead.date_closed = datetime(2021, 9, 8)
        self.assertEqual(self.crm_lead.days_exceeding_closing, 30)

    def test_compute_days_to_convert(self):
        self.crm_lead.date_conversion = datetime(2021, 10, 8)
        self.crm_lead.create_date = datetime(2021, 9, 8)
        self.assertEqual(self.crm_lead.days_to_convert, 30)

    def test_compute_won_status(self):
        self.assertEqual(self.crm_lead.won_status, 'pending')

        self.crm_lead.active = True
        self.crm_lead.stage_id = self.env.ref("crm.stage_lead4").id
        self.assertEqual(self.crm_lead.won_status, 'won')

        self.crm_lead.active = False
        self.crm_lead.probability = 0
        self.assertEqual(self.crm_lead.won_status, 'lost')
