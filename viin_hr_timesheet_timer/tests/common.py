from odoo.tests.common import SavepointCase


class Common(SavepointCase):
    
    def setUp(self):
        super(Common, self).setUp()
        
        self.task1 = self.env.ref('project.project_task_1')
        self.task2 = self.env.ref('project.project_task_2')
        
        self.user_demo = self.env.ref('base.user_demo')
        self.user_admin = self.env.ref('base.user_admin')
        
        self.timesheet_1 = self.env.ref('hr_timesheet.working_hours_testing')
