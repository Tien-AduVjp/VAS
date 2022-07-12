from odoo.tests.common import tagged, Form
from odoo.exceptions import ValidationError
from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestProjectTask(TestCommon):

    def test_onchange_project_id_load_git(self):
        self.project1.git_repository_id = self.git_repo1
        self.project2.git_repository_id = self.git_repo2

        with Form(self.task1) as task_form:
            task_form.project_id = self.project2
        task = task_form.save()
        self.assertEqual(task.git_repository_id.id, self.git_repo2.id)

    def test_01_onchange_git_repository_id(self):
        self.git_branch1.is_default = True

        with Form(self.task1) as task_form:
            task_form.git_repository_id = self.git_repo1
        task = task_form.save()
        self.assertEqual(task.git_branch_id.id, self.git_branch1.id)

    def test_02_onchange_git_repository_id(self):
        with Form(self.task1) as task_form:
            task_form.git_repository_id = self.git_repo1
        task = task_form.save()
        self.assertFalse(bool(task.git_branch_id))

    def test_03_onchange_git_repository_id(self):
        self.task1.git_repository_id = self.git_repo1
        self.task1.write({
            'git_repository_id': self.git_repo1.id,
            'git_branch_id': self.git_branch1.id
        })

        with Form(self.task1) as task_form:
            task_form.git_repository_id = self.env['git.repository']
        task = task_form.save()
        self.assertFalse(bool(task.git_branch_id))

    def test_01_check_constrains_git_repository_id_git_branch_id(self):
        with self.assertRaises(ValidationError):
            self.task1.git_branch_id = self.git_branch1

    def test_02_check_constrains_git_repository_id_git_branch_id(self):
        self.task1.git_repository_id = self.git_repo1
        with self.assertRaises(ValidationError):
            self.task1.git_branch_id = self.git_branch2
