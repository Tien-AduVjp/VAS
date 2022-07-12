from odoo.tests.common import tagged
from .test_common import TestCommon


@tagged('-at_install', 'post_install')
class TestGitRepository(TestCommon):

    def test_compute_projects_count(self):
        self.project1.git_repository_id = self.git_repo1
        self.assertEqual(self.git_repo1.projects_count, 1)

    def test_compute_tasks_count(self):
        self.task1.git_repository_id = self.git_repo1
        self.task2.git_repository_id  = self.git_repo1
        self.assertEqual(self.git_repo1.tasks_count, 2)
