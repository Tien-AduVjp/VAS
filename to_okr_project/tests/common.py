from odoo.tests.common import TransactionCase


class Common(TransactionCase):

    def setUp(self):
        super(Common, self).setUp()
        self.project_1 = self.env.ref('project.project_project_1')
        self.project_2 = self.env.ref('project.project_project_2')

        # Task of project 1
        self.project_task_1 = self.env.ref('project.project_task_1')
        self.project_task_2 = self.env.ref('project.project_task_25')

        # Task of project 2
        self.project_task_3 = self.env.ref('project.project_task_12')

        # OKR
        self.okr_1 = self.env['okr.node'].create({
            'name': 'OKR Node Test 1',
            'type': 'committed',
        })
        self.okr_2 = self.env['okr.node'].create({
            'name': 'OKR Node Test 2',
            'type': 'committed',
        })
