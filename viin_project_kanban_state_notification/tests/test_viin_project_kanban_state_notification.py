from unittest.mock import patch
from odoo.tests.common import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestViinProjectKanBanStateNotification(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestViinProjectKanBanStateNotification, cls).setUpClass()
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.user_demo = cls.env.ref('base.user_demo')
        
        cls.project_1 = cls.env.ref('project.project_project_1')
        cls.task_1 = cls.project_1.task_ids[0]
        
        cls.project_1.user_id = cls.user_admin

    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_post')
    def test_01_message_post(self, message_post):
        # case 1:
        self.task_1.with_user(self.user_demo).kanban_state = 'done'
        message_post.assert_called()
        
        call_args = message_post.call_args[1]    
        self.assertIn(self.user_admin.partner_id.id, call_args['partner_ids'])
        self.assertIn('@Mitchell Admin', call_args['body'])
    
    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_post')
    def test_02_message_post(self, message_post):
        # case 2:
        self.task_1.with_user(self.user_admin).kanban_state = 'done'
        message_post.assert_called()
        
        call_args = message_post.call_args[1]
        self.assertNotIn(self.user_admin.partner_id.id, call_args.get('partner_ids', []))
        self.assertNotIn('@Mitchell Admin', call_args.get('body', ''))
