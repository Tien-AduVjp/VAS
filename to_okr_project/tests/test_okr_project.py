from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestOkrProject(Common):

    def test_01_check_okr_project(self):
        """
        Input:
            OKR 1,
            Project 1,
            Task 1 of Project 1,
            Task 1 assigned with OKR 1
        """
        self.project_task_1.write({'okr_node_id': self.okr_1.id})

        self.assertEqual(self.project_task_1.okr_node_id, self.okr_1)
        self.assertEqual(self.okr_1.projects_count, 1)
        self.assertEqual(self.okr_1.project_tasks_count, 1)
        self.assertEqual(self.project_1.okr_nodes_count, 1)

        self.assertIn(self.okr_1.id, self.project_1.okr_node_ids.ids)
        self.assertIn(self.project_1.id, self.okr_1.project_ids.ids)
        self.assertIn(self.project_task_1.id, self.okr_1.project_task_ids.ids)

    def test_02_check_okr_project(self):
        """
        Input:
            OKR 1,
            Project 1 and Project 2,
            Task 1 of Project 1, Task 2 of Project 2
            Task 1 and Task 2 assigned with OKR 1
        """
        self.project_task_1.write({'okr_node_id': self.okr_1.id})
        self.project_task_3.write({'okr_node_id': self.okr_1.id})

        self.assertEqual(self.project_task_1.okr_node_id, self.okr_1)
        self.assertEqual(self.project_task_3.okr_node_id, self.okr_1)
        self.assertEqual(self.okr_1.projects_count, 2)
        self.assertEqual(self.okr_1.project_tasks_count, 2)
        self.assertEqual(self.project_1.okr_nodes_count, 1)
        self.assertEqual(self.project_2.okr_nodes_count, 1)

        self.assertIn(self.okr_1.id, self.project_1.okr_node_ids.ids)
        self.assertIn(self.okr_1.id, self.project_2.okr_node_ids.ids)
        self.assertIn(self.project_1.id, self.okr_1.project_ids.ids)
        self.assertIn(self.project_2.id, self.okr_1.project_ids.ids)
        self.assertIn(self.project_task_1.id, self.okr_1.project_task_ids.ids)
        self.assertIn(self.project_task_3.id, self.okr_1.project_task_ids.ids)

    def test_03_check_okr_project(self):
        """
        Input:
            OKR 1, OKR 2
            Project 1,
            Task 1 and Task 2 of Project 1,
            Task 1 assigned with OKR 1, Task 2 assigned with OKR 2
        """
        self.project_task_1.write({'okr_node_id': self.okr_1.id})
        self.project_task_2.write({'okr_node_id': self.okr_2.id})

        self.assertEqual(self.project_task_1.okr_node_id, self.okr_1)
        self.assertEqual(self.project_task_2.okr_node_id, self.okr_2)
        self.assertEqual(self.okr_1.projects_count, 1)
        self.assertEqual(self.okr_2.projects_count, 1)
        self.assertEqual(self.okr_1.project_tasks_count, 1)
        self.assertEqual(self.okr_2.project_tasks_count, 1)
        self.assertEqual(self.project_1.okr_nodes_count, 2)

        self.assertIn(self.okr_1.id, self.project_1.okr_node_ids.ids)
        self.assertIn(self.okr_2.id, self.project_1.okr_node_ids.ids)
        self.assertIn(self.project_1.id, self.okr_1.project_ids.ids)
        self.assertIn(self.project_1.id, self.okr_2.project_ids.ids)
        self.assertIn(self.project_task_1.id, self.okr_1.project_task_ids.ids)
        self.assertIn(self.project_task_2.id, self.okr_2.project_task_ids.ids)

    def test_04_check_okr_project(self):
        """
        Unlink OKRs from projects and tasks
        """
        self.project_task_1.write({'okr_node_id': self.okr_1.id})
        self.assertIn(self.project_1, self.okr_1.project_ids)

        self.project_task_1.write({'okr_node_id': False})
        self.assertNotIn(self.project_1, self.okr_1.project_ids)

    def test_05_check_okr_project(self):
        """
        Remove OKRs while linking to projects and tasks, OKRs in draft state
        """
        self.project_task_1.write({'okr_node_id': self.okr_1.id})
        self.okr_1.unlink()


    def test_06_check_access_task_associated_okr(self):
        """
        Input:
                project_task_test set Key Result with okr_1
                project_task_test set Project with project_test
                project_test set as private project

        Output:

                Internal Users able to see okr_1 can access project_task_test
        """
        self.project_test = self.env['project.project'].create({
                'name':'Project Test',
                'privacy_visibility': 'followers',
        })
        self.project_task_test = self.env['project.task'].create({
                'name':'Task Test',
                'project_id': self.project_test.id,
                'okr_node_id': self.okr_1.id,
        })

        self.internal_user = self.env.ref('base.user_demo')
        # Internal Users can read project task associated with OKR
        self.assertTrue(self.project_task_test.with_user(self.internal_user).check_access_rights('read'))
        self.assertTrue(self.project_test.with_user(self.internal_user).check_access_rights('read'))
