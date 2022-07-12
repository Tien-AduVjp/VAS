from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, tagged
from .common import Common


@tagged('post_install', '-at_install')
class TestToOkr(Common):

    def test_unlink(self):
        self.okr_node_root.button_confirm()
        with self.assertRaises(UserError):
            self.okr_node_root.unlink()

    def test_constraint_point(self):
        self.okr_node_root.points = 1
        with self.assertRaises(ValidationError):
            self.okr_node_root.points = -0.5
        with self.assertRaises(ValidationError):
            self.okr_node_root.points = 2

    def test_check_constrains_name(self):
        self.okr_node_root.name = 'Test'
        with self.assertRaises(ValidationError):
            self.okr_node_root.name = 'T' * 101

    def test_compute_progress(self):
        self.okr_node_root.points = 0.5
        self.assertEqual(self.okr_node_root.progress, 50)
        self.okr_node_root.points = 1
        self.assertEqual(self.okr_node_root.progress, 100)

    def test_check_parent(self):
        self.okr_node_root.parent_id = False
        with self.assertRaises(UserError):
            self.okr_node_root.mode = 'department'
        with self.assertRaises(UserError):
            self.okr_node_root.mode = 'employee'

        self.okr_node_root.parent_id = self.env['okr.node'].create({
            'name': 'OKR 2'
        })
        self.okr_node_root.mode = 'department'
        self.okr_node_root.mode = 'employee'

    def test_compute_result(self):
        self.okr_node_root.type = 'aspirational'
        self.okr_node_root.points = 0.7
        self.assertEqual(self.okr_node_root.result, 'successful')

        self.okr_node_root.type = 'committed'
        self.okr_node_root.points = 0.7
        self.assertEqual(self.okr_node_root.result, 'failed')

        self.okr_node_root.points = 1
        self.assertEqual(self.okr_node_root.result, 'successful')

    def test_default_mode(self):
        okr_node1 = self.env['okr.node'].with_user(self.okr_manager).create({
            'name': 'okr node1'
        })
        okr_node2 = self.env['okr.node'].with_user(self.hr_manager_user).create({
            'name': 'okr child 1',
            'parent_id': okr_node1.id
        })
        okr_node3 = self.env['okr.node'].with_user(self.user1).create({
            'name': 'okr child 2',
            'parent_id': okr_node2.id
        })
        self.assertEqual(okr_node1.mode, 'company')
        self.assertEqual(okr_node2.mode, 'department')
        self.assertEqual(okr_node3.mode, 'employee')

    def test_parent_id_required_01(self):
        # TC8: test parent_id required
        with self.assertRaises(AssertionError):
            with Form(self.env['okr.node'].with_user(self.hr_manager_user)) as okr_form:
                okr_form.name = 'node with department form'
                okr_form.mode = 'department'
                okr_form.department_id = self.hr_department
    
    def test_parent_id_required_02(self):
        # TC9:
        with self.assertRaises(AssertionError):
            with Form(self.env['okr.node'].with_user(self.hr_manager_user)) as okr_form:
                okr_form.mode = 'employee'
                okr_form.name = 'node with department form'
                self.assertEqual(okr_form.user_id, self.hr_manager_user)

    def test_01_compute_points(self):
        """Test case of reset and readonly (on form) of points field when there is okr child"""
        example_okr_node = self.env['okr.node'].with_context(tracking_disable=True).with_user(self.okr_manager).create({
            'name': 'example OKR node',
            'type': 'aspirational',
            'points': 1.
        })
        example_okr_node.write({
            'child_ids': [(0, 0, {
                'name': 'example OKR node',
                'type': 'aspirational',
                'points': 0.0
                })]
            })
        self.assertEqual(example_okr_node.points, 0.0)
        with Form(example_okr_node.with_user(self.okr_manager)) as okr_form:
            # test cannot edit points when okr already has key result on the form view
            with self.assertRaises(AssertionError):
                okr_form.points = 1

    def test_02_compute_points(self):
        """Test only calculates points when okr child has confirmed status"""
        okr_node1 = self.okr_node_root.with_user(self.okr_manager)
        child_ids = self.child_ids.with_user(self.okr_manager)

        okr_node1.child_ids = self.child_ids

        child_ids[0].state = 'confirmed'
        child_ids[0].weight = 50
        child_ids[0].points = 0.5

        child_ids[1].state = 'draft'
        child_ids[1].weight = 50
        child_ids[1].points = 1

        self.assertEqual(okr_node1.points, 0.5)

    def test_03_compute_points(self):
        """
           Case 1: test case does not enter weight for all okr children,
           Case 2: all okr children have non-zero weight
           Case 3: okr child contains both zero and non-zero weight okr
           Case 4: confirm recalculate points of parent okr when changing status of child okr
        """
        okr_node1 = self.okr_node_root.with_user(self.okr_manager)
        child_ids = self.child_ids.with_user(self.okr_manager)
        okr_node1.child_ids = self.child_ids

        child_ids.button_confirm()

        # case 1:
        child_ids[0].points = 1
        child_ids[1].points = 0.5
        child_ids[2].points = 0.7
        self.assertEqual(okr_node1.points, 0.73)

        # case 2:
        child_ids[0].weight = 50
        child_ids[1].weight = 30
        child_ids[2].weight = 20
        self.assertEqual(okr_node1.points, 0.79)

        # case 3:
        child_ids[0].weight = 50
        child_ids[1].weight = 0
        child_ids[2].weight = 20
        self.assertEqual(okr_node1.points, 0.91)

        # case 4:
        child_ids[0].weight = 50
        child_ids[1].weight = 20
        child_ids[2].weight = 30

        child_ids[0].points = 1
        child_ids[1].points = 0.5
        child_ids[2].points = 0.5

        child_ids[0].state = 'draft'
        self.assertEqual(okr_node1.points, 0.5)

    def test_01_check_parent_required(self):
        """
        check parent require value when create or edit record
        Case 1: when create a stand-alone record when mode is company 
        Case 2: when create a stand-alone record when mode is department or employee
        Case 3: when create record from parent okr record form with mode is company
        Case 4: when create record from parent okr record form with mode is department
        """
        # Case 1:
        with Form(self.env['okr.node'].with_user(self.hr_manager_user)) as okr_form:
            okr_form.name = 'node with company mode'
            okr_form.mode = 'company'
            self.assertFalse(
                okr_form._get_modifier('parent_id', 'required'),
                "'when mode is company parent_id is not required'"
                )

    def test_02_check_parent_required(self):
        with Form(self.env['okr.node'].with_user(self.hr_manager_user)) as okr_form:
            okr_form.name = 'node with department mode'
            okr_form.mode = 'department'
            self.assertTrue(okr_form._get_modifier('parent_id', 'required'))
            okr_form.mode = 'company'  # to avoid error with other required fields when saving form upon with exit

    def test_03_check_parent_required(self):
        with Form(self.env['okr.node'].with_user(self.hr_manager_user)) as okr_form:
            okr_form.name = 'node with employee mode'
            okr_form.mode = 'employee'
            self.assertTrue(
                okr_form._get_modifier('parent_id', 'required'),
                "'when mode is employee parent_id is required'"
                )
            okr_form.mode = 'company'  # to avoid error with other required fields when saving form upon with exit
