from odoo.tests.common import tagged
from .test_common import TestCommon


@tagged('-at_install', 'post_install')
class TestGitBranch(TestCommon):

    def test_compute_tasks_count(self):
        self.task1.write({
            'git_repository_id': self.git_repo1.id,
            'git_branch_id': self.git_branch1
        })
        self.task2.write({
            'git_repository_id': self.git_repo1.id,
            'git_branch_id': self.git_branch1
        })
        self.assertEqual(self.git_branch1.tasks_count, 2)

    def test_compute_projects_count(self):
        self.task1.write({
            'git_repository_id': self.git_repo1.id,
            'git_branch_id': self.git_branch1
        })
        self.task3.write({
            'git_repository_id': self.git_repo1.id,
            'git_branch_id': self.git_branch1
        })
        self.assertEqual(self.git_branch1.projects_count, 2)
