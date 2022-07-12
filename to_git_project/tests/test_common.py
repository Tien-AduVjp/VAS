from odoo.tests.common import SavepointCase


class TestCommon(SavepointCase):
    
    def setUp(self):
        super(TestCommon, self).setUp()
        
        self.git_repo1 = self.env['git.repository'].create({
            'name': 'repository1 test',
            'remote_url': 'url 01',
            'domain_name' : 'test 1'
        })
        self.git_repo2 = self.env['git.repository'].create({
            'name': 'repository2 test',
            'remote_url': 'url 02',
            'domain_name': 'test 2'
        })
        
        self.git_branch1 = self.env['git.branch'].with_context(skip_check_branch_name=True).create({
            'name': 'repo1 branch 1',
            'repository_id': self.git_repo1.id
        })
        self.git_branch2 = self.env['git.branch'].with_context(skip_check_branch_name=True).create({
            'name': 'repo2 branch 2',
            'repository_id': self.git_repo2.id
        })
        
        self.project1 = self.env.ref('project.project_project_1')
        self.project2 = self.env.ref('project.project_project_2')
        
        # task1, task2 in project1
        # task3, task4 in project2
        self.task1 = self.env.ref('project.project_task_1')
        self.task2 = self.env.ref('project.project_task_2')
        self.task3 = self.env.ref('project.project_task_8')
        self.task4 = self.env.ref('project.project_task_9')
