from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from . import common

@tagged('post_install','-at_install')
class TestMaintenanceRequest(common.Common):

    def setUp(self):
        super(TestMaintenanceRequest, self).setUp()       
        self.technical_user_id = self.env['res.users'].create({
            'name':'Viin Technical User',
            'login':'viin_technical_user_test_01',
            'email':'viin_technical_user@example.viindoo.com'
        })
        self.maintenance_request_01 = self.env['maintenance.request'].create({
            'name':'Request maintenance Equipment Test 01',
            'equipment_id':self.equipment_test_01.id,
            'maintenance_type':'preventive',
            'maintenance_team_id':self.ref('maintenance.equipment_team_maintenance'),
            'user_id':self.technical_user_id.id,
            'owner_user_id':self.env.user.id,
            'schedule_date':fields.date.today() + timedelta(days =  10)
        })

    def test_compute_date_to_notify(self):
        """ *Principle:
            date_to_notify  = maintenance_request.schedule_date - equipment.days_to_notify          
        """        
        self.assertEqual(self.maintenance_request_01.date_to_notify,fields.date.today() + timedelta(days = 3))
        # date_to_notify should recompute if days to notify of equipment change.
        self.equipment_category_test_01.update({
            'days_to_notify': 5
        })
        self.assertEqual(self.maintenance_request_01.date_to_notify,fields.date.today() + timedelta(days = 5))
        # date_to_notify should recompute if schedule date of request change.
        self.maintenance_request_01.update({
            'schedule_date':fields.date.today() + timedelta(days =  6)
        })
        self.assertEqual(self.maintenance_request_01.date_to_notify,fields.date.today() + timedelta(days = 1))

    def test_01_cron_notify_maintenance(self):
        """
            A notification should be send if date to notify is a day in past.
        """
        self.maintenance_request_01.update({
            'schedule_date':fields.date.today() + timedelta(days =  6)
        })
        self.env.ref('to_maintenance_notification.ir_cron_scheduler_send_email').method_direct_trigger()
        self.assertTrue(self.maintenance_request_01.notified)

    def test_02_cron_notify_maintenance(self):
        """
            A notification should be send if date to notify is today.
        """
        self.maintenance_request_01.update({
            'schedule_date':fields.date.today() + timedelta(days =  7)
        })
        self.env.ref('to_maintenance_notification.ir_cron_scheduler_send_email').method_direct_trigger()
        self.assertTrue(self.maintenance_request_01.notified)

    def test_03_cron_notify_maintenance(self):
        """
            A notification cannot send if date to notify is furture day.
        """
        self.maintenance_request_01.update({
            'schedule_date':fields.date.today() + timedelta(days =  8)
        })
        self.env.ref('to_maintenance_notification.ir_cron_scheduler_send_email').method_direct_trigger()
        self.assertFalse(self.maintenance_request_01.notified)
