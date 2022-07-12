from odoo.tests import Form, tagged
from odoo.exceptions import ValidationError, UserError
from .common import TestRepairTimesheetCommon


@tagged('-at_install', 'post_install')
class TestRepairTimesheet(TestRepairTimesheetCommon):
    """
        service_policy
            ordered_timesheet:      Ordered quantities
            delivered_timesheet:    Timesheets on tasks
            delivered_manual:       Milestones (manually set quantities on order)

        service_tracking:
            no                      Dont create task
            task_global_project     Create a task in an existing project
            task_in_project        Create a task in sales order's project
            project_only            Create a new project but no task

        expense_policy:
            no                      No
            cost                    At cost
            sales_price             Sales price
    """

    def test_01_repair_has_repair_fee_create_project(self):
        """
            Input:
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
    
            Expect:
            A project that linked to the repair order is created
            A related task is created on this project
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.after_sales_services_project.id
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        self.assertTrue(bool(repair_order.project_ids[0]))
        self.assertFalse(bool(repair_order.project_ids[0].repair_fee_line_id))
        self.assertTrue(bool(repair_order.tasks_ids))
        self.assertTrue(bool(repair_order.tasks_ids.repair_fee_line_id))
        self.assertEqual(repair_order.tasks_count, 1)
    
    def test_02_repair_has_repair_fee_2_products(self):
        """
            Input:
                product 1:
                    service_tracking = task_global_project
                    project 1
                product 2:
                    service_tracking = task_global_project
                    project 2
    
            Expect:
                2 new projected, which are linked to the repair order, are created
                2 new related tasks are created on the projects, respectively
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.after_sales_services_project.id
        })
    
        # The second service product
        self.service_product_2.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('project.project_project_1').id
        })
    
        repair_order = self._create_repair_order([self.service_product, self.service_product_2])
    
        related_project = repair_order.project_ids
    
        self.assertEqual(len(related_project), 2, "There should be created 2 projects.")
        self.assertFalse(bool(related_project[0].repair_fee_line_id))
        self.assertFalse(bool(related_project[1].repair_fee_line_id))
        self.assertEqual(repair_order.tasks_count, 2)
        self.assertTrue(bool(repair_order.tasks_ids[0].repair_fee_line_id))
        self.assertTrue(bool(repair_order.tasks_ids[1].repair_fee_line_id))
    
    def test_03_repair_has_repair_fee_3(self):
        """
            Input:
                'service_policy': 'delivered_timesheet',
                'service_tracking': 'project_only' (Create project but not create task)
    
            Expect:
                A project is created but no task is found.
        """
    
        self.service_product.write({'service_tracking': 'project_only'})
    
        repair_order = self._create_repair_order([self.service_product])
    
        related_project = repair_order.project_ids
    
        self.assertTrue(bool(related_project.repair_fee_line_id))
        self.assertTrue(bool(related_project))
        self.assertEqual(repair_order.tasks_count, 0)
        self.assertFalse(bool(repair_order.tasks_ids))
    
    def test_04_extension_for_test_03(self):
        """
            Input:
                2 products with 'service_tracking': 'project_only'
    
            Expect:
                Only 1 project is created
                No task is created
        """
    
        self.service_product.write({'service_tracking': 'project_only'})
    
        # The second service product
        service_product_copy = self.service_product.copy()
    
        repair_order = self._create_repair_order([self.service_product, service_product_copy])
    
        related_project = repair_order.project_ids
    
        self.assertEqual(
            len(related_project),
            1,
            "There should only be created 1 projects without any task."
        )
        self.assertTrue(bool(related_project.repair_fee_line_id))
        self.assertFalse(bool(repair_order.tasks_ids))
    
    def test_04_1_different_service_tracking(self):
        """
            Input:
                1 product: Create a task in an existing project
                1 product: Create a new project but no task
    
            Expect:
                2 projects are created. 1 of them has the same name as repair order does
                1 task is created that has the same name as repair order
        """
    
        self.service_product.write({'service_tracking': 'project_only'})
        self.service_product_2.write({
            'service_tracking': 'task_global_project',
            'project_id': self.after_sales_services_project.id
        })
    
        repair_order = self._create_repair_order([self.service_product, self.service_product_2])
    
        related_project = repair_order.project_ids
        related_tasks = repair_order.tasks_ids
    
        self.assertEqual(len(related_project), 2, "There should be 2 tasks created.")
        self.assertEqual(len(related_tasks), 1, "There should only be 1 task created.")
    
        project_same_name_repair_order = related_project.filtered(
            lambda proj: proj.name == repair_order.name
        )
        task_same_name_repair_order = related_tasks.filtered(
            lambda task: repair_order.name in task.name
        )
    
        self.assertTrue(
            bool(project_same_name_repair_order),
            "Project name should be identical with repair order name."
        )
        self.assertTrue(
            bool(task_same_name_repair_order),
            "Task name should include the name of the repair order."
        )
    
        self.assertTrue(bool(project_same_name_repair_order.repair_fee_line_id))
    
    def test_05_06_new_task_subtask_created_after_repair_order_confirmed(self):
        """
            Case 05:
                Product:    service tracking = 'Create a new project but no task'
                Create a repair order using this product
                    => generate a new project with the same name
                Manually create a task on this project.
    
                Expect:
                    repair fee record (project) =  repair fee record (task)
    
            Case 06:
                Create a subtask on the task above
    
                Expect:
                    repair fee record (task) =  repair fee record (subtask)
        """
        self.service_product.write({'service_tracking': 'project_only'})
    
        repair_order = self._create_repair_order([self.service_product])
    
        related_project = repair_order.project_ids[0]
    
        task = self.env['project.task'].create({
            'name': 'Test task',
            'project_id': related_project.id,
            'user_id': self.env.uid,
            'company_id': self.env.company.id
        })
    
        self.assertEqual(
            related_project.repair_fee_line_id.id,
            task.repair_fee_line_id.id,
            ("The repair fee records are different. "
             "Manually created task on this project should have the same data of repair fee.")
        )
    
        subtask = self.env['project.task'].create({
            'parent_id': task.id,
            'name': 'Test Sub Task',
            'project_id': related_project.id,
            'user_id': self.env.uid,
            'company_id': self.env.company.id,
        })
    
        self.assertEqual(task.subtask_count, 1)
        self.assertEqual(task.child_ids[0].id, subtask.id)
        self.assertEqual(subtask.parent_id.id, task.id)
        self.assertEqual(
            task.repair_fee_line_id,
            subtask.repair_fee_line_id,
            "Expected: repair fee line (subtask) == repair fee line (task)."
        )
    
    def test_07_new_sub_task_created_after_repair_order_confirmed(self):
        """
            Step 1: do case 05
            Step 2: Update a task and select a parent task.
                    This parent task is currently being linked to a repair fee line
    
            Expect:
                After editing, the sub task is now linked to the same repair fee line
        """
    
        self.service_product.write({'service_tracking': 'project_only'})
    
        repair_order = self._create_repair_order([self.service_product])
    
        related_project = repair_order.project_ids
    
        task = self.env['project.task'].create({
            'name': 'Test task',
            'project_id': related_project.id,
            'user_id': self.env.uid,
            'company_id': self.env.company.id
        })
    
        task_as_subtask = self.env.ref('sale_timesheet.project_task_3')
    
        self.assertFalse(bool(task_as_subtask.repair_fee_line_id))
    
        task_as_subtask.write({'parent_id': task.id})
    
        self.assertTrue(bool(task_as_subtask.repair_fee_line_id))
    
    def test_08_delete_task_has_repair_fee_line(self):
        self.service_product.write({'service_tracking': 'project_only'})
    
        repair_order = self._create_repair_order([self.service_product])
    
        related_project = repair_order.project_ids[0]
    
        task = self.env['project.task'].create({
            'name': 'Test task',
            'project_id': related_project.id,
            'user_id': self.env.uid,
            'company_id': self.env.company.id
        })
    
        with self.assertRaises(ValidationError):
            task.unlink()
    
    def test_09(self):
        """
            Input:
                Repair order, which has repair fee, has UOM as Units
                Project has UOM time that is set as Hours (by default)
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product])
        related_project = repair_order.project_ids[0]
    
        self.assertEqual(
            related_project.tasks[0].planned_hours,
            1,
            "Planned Hours should be converted equivalent to the quantity on the repair fee."
        )
    
    def test_10(self):
        """
            Input:
                Repair order, which has repair fee, has UOM as Days
                Project has UOM time that is set as Hours (by default)
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        # Create repair order that has uom as Days
        repair_order = self.env['repair.order'].create({
            'product_id': self.product_to_repair.id,
            'product_uom': self.product_to_repair.uom_id.id,
            'product_qty': 1,
            'partner_id': self.partner_1.id,
            'create_invoice': True,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'user_id': self.env.uid,
            'company_id': self.env.company.id,
            'fees_lines': [
                (0, 0, {
                    'name': self.service_product.name,
                    'product_id': self.service_product.id,
                    'product_uom_qty': 1,
                    'product_uom': self.env.ref('uom.product_uom_day').id,
                    'product_uom_category_id': self.env.ref('uom.uom_categ_wtime').id,
                    'price_unit': 50,
                    'tax_id': False
                })
            ]
        })
    
        repair_order.action_validate()
    
        related_project = repair_order.project_ids[0]
        self.assertEqual(
            related_project.tasks[0].planned_hours,
            8,
            "Planned hours should be converted from Days to Hours."
        )
    
    def test_11_log_timesheet(self):
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        # repair order => repair fee => qty delivered
        self.assertEqual(repair_order.fees_lines[0].qty_delivered, 0)
    
        # Log a timesheet
        timesheet = self._task_update_timesheet(
            name='Test timesheet',
            task=repair_order.tasks_ids[0],
            time_start=9,
        )
    
        self.assertEqual(self.service_product.expense_policy, 'no')
        self.assertFalse(bool(repair_order.analytic_account_id))
    
        # Because repair order has no analytic_account_id
        # Therefore:
        self.assertEqual(repair_order.timesheet_count, 0)
        self.assertFalse(bool(repair_order.timesheet_ids))
    
        self.assertEqual(
            repair_order.tasks_ids[0].timesheet_ids[0].id,
            timesheet.id
        )
    
        self.assertEqual(repair_order.fees_lines[0].qty_delivered, 1)
    
    def test_12_number_of_projects_linked_to_repair_order(self):
        """
            Input:
                1 project with service_tracking = project_only (Create a new project but no task)
                1 project with default settings:
                    service_policy:        ordered_timesheet (Ordered quantities)
                    service_tracking:      no                (Don't create task)
        """
    
        self.service_product.write({'service_tracking': 'project_only'})
        service_product_2 = self.env.ref('sale_timesheet.product_service_order_timesheet')
        service_product_2.write({
            'service_policy': 'ordered_timesheet',
            'service_tracking': 'no',
        })
    
        repair_order = self._create_repair_order([self.service_product, service_product_2])
    
        self.assertEqual(len(repair_order.project_ids), 2)
    
    def test_13_number_of_tasks_linked_to_repair_order(self):
        """
            Input:
                1 task is created for repair fee on an existed project
                1 task is created on a new project, that is created for repair fee
    
            - Input: repair liên kết đến 2 task:
                + 1 task được tạo mới cho cho repair fee trong 1 project có sẵn
                + 1 task được tạo trên project mới được tạo ra cho repair fee
            - Expected Result: repair có 2 task
        """
    
        self.service_product.write({'service_tracking': 'project_only'})
        self.service_product_2.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product, self.service_product_2])
    
        self.assertEqual(len(repair_order.project_ids), 2)
        self.assertEqual(len(repair_order.tasks_ids), 1)
    
        # Adding one more task on project and check if it is linked to repair fee
        #     is already tested in test 05
    
    def test_14_number_of_timesheet_linked_repair_order(self):
        """
            Input: repair liên kết đến 3 timesheet:
                + 2 timesheet có liên kết đến1 repair fee
                + 1 timesheet có liên kết đến 1 repair fee khác
            - Expected Result: repair có 3 timesheet
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
        self.service_product_2.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product, self.service_product_2])
    
        # Log a timesheet first time
        self._task_update_timesheet(
            name='Preparation',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
        self._task_update_timesheet(
            name='Bug Fixing',
            task=repair_order.tasks_ids[0],
            time_start=10,
        )
    
        # Log a timesheet second time
        self._task_update_timesheet(
            name='Create Module A',
            task=repair_order.tasks_ids[1],
            time_start=9,
        )
    
        self.assertEqual(repair_order.timesheet_count, 0)
        self.assertFalse(bool(repair_order.analytic_account_id))
    
        self.assertTrue('Preparation' in repair_order.tasks_ids.timesheet_ids.mapped('name'))
        self.assertTrue('Bug Fixing' in repair_order.tasks_ids.timesheet_ids.mapped('name'))
        self.assertTrue('Create Module A' in repair_order.tasks_ids.timesheet_ids.mapped('name'))
    
    def test_15_create_invoice_without_option_to_create_invoices(self):
        """
            Input:
                Create repair order that has:
                    To Create Invoice field = False
                    Repair Line
                    Repair Fee
                        Create timesheet for this repair fee
            Expect:
                Can't create invoice for this repair order
        """
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order(
            product_list=[self.service_product],
            bool_create_invoice=False,
        )
    
        with self.assertRaises(UserError):
            self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.invoice_count, 0)
    
    def test_16_01_create_invoice(self):
        """
            Product:
                service_policy:      delivered_timesheet (Timesheets on tasks)
                service_tracking:    task_global_project (Create a task in an existing project)
    
            Input:
                Create repair order that has:
                    1 Repair Line
                    1 Repair Fee
                Create an invoice for this repair order
            Expect:
                After invoiced, the status of the repair fee is 'no',
                    because there is no log timesheet on it
                invoice order line has data of repair line
                invoice order line has no data of repair fee
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product], True)
    
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.invoice_id.repair_ids[0].id, repair_order.id)
        self.assertEqual(repair_order.invoice_count, 1)
        self.assertEqual(
            len(repair_order.invoice_id.invoice_line_ids),
            1,
            "There should only be 1 invoice line: product repair line"
        )
        self.assertEqual(repair_order.fees_lines[0].invoice_status, 'no')
        self.assertTrue(bool(repair_order.invoice_id.invoice_line_ids[0].repair_line_ids))
        self.assertFalse(bool(repair_order.invoice_id.invoice_line_ids[0].repair_fee_ids))
        self.assertFalse(bool(repair_order.invoice_id.invoice_line_ids[0].repair_fee_line_ids))
    
    def test_16_02_create_invoice(self):
        """
            Product:
                service_policy:      delivered_timesheet (Timesheets on tasks)
                service_tracking:    task_global_project (Create a task in an existing project)
    
            Input:
                Create repair order that has:
                    1 Repair Line
                    1 Repair Fee
                Add a log timesheet to the repair fee (corresponding task)
                Create an invoice for this repair order
            Expect:
                After logged timesheet, the status of the repair fee is 'to invoice'
                After invoiced, the status of the repair fee is 'invoiced'
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        # Create Repair Order
        repair_order = self._create_repair_order([self.service_product], True)
    
        self.assertEqual(repair_order.fees_lines[0].invoice_status, 'no')
    
        # Log Timesheet
        self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        self.assertEqual(repair_order.fees_lines[0].invoice_status, 'to invoice')
    
        # Create Invoice
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.fees_lines[0].invoice_status, 'invoiced')
        self.assertTrue(bool(repair_order.invoice_id.invoice_line_ids[0].repair_line_ids))
        self.assertFalse(bool(repair_order.invoice_id.invoice_line_ids[1].repair_line_ids))
    
        self.assertFalse(bool(repair_order.invoice_id.invoice_line_ids[0].repair_fee_ids))
        self.assertTrue(bool(repair_order.invoice_id.invoice_line_ids[1].repair_fee_ids))
    
        self.assertFalse(bool(repair_order.invoice_id.invoice_line_ids[0].repair_fee_line_ids))
        self.assertTrue(bool(repair_order.invoice_id.invoice_line_ids[1].repair_fee_line_ids))
    
    def test_16_03_create_invoice(self):
        """
            Product:
                service_policy:      delivered_timesheet (Timesheets on tasks)
                service_tracking:    task_global_project (Create a task in an existing project)
    
            Input:
                Create repair order that has:
                    1 Repair Line
                    1 Repair Fee
                1) Create an invoice for this repair order
                Add a log timesheet to the repair fee (corresponding task)
                2) Create an invoice for this repair order
            Expect:
                After 1)
                    + 1 invoice is created
                    + the invoice has only 1 invoice line for the repair line product
                    + No invoice line for the  repair fee product
                After invoiced again 2)
                    + 1 more invoice is created for the repair fee
                    + this new invoice has no data of the repair line
        """
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product], True)
    
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.fees_lines[0].invoice_status, 'no')
        self.assertEqual(len(repair_order.invoice_ids), 1, "1 invoice should have been created.")
        self.assertEqual(
            len(repair_order.invoice_ids[0].invoice_line_ids),
            1,
            "There should be only 1 invoice line."
        )
        self.assertEqual(
            repair_order.operations[0].product_id.id,
            repair_order.invoice_ids[0].invoice_line_ids[0].product_id.id,
            "Only the repair line (operation) has been invoiced, not the repair fee."
        )
    
        # Log Timesheet
        self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        self.assertEqual(repair_order.fees_lines[0].invoice_status, 'to invoice')
    
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.invoice_count, 2)
        self.assertEqual(repair_order.fees_lines[0].invoice_status, 'invoiced')
    
        self.assertEqual(
            len(repair_order.invoice_id.invoice_line_ids),
            1,
            "The second invoice should only have 1 invoice line."
        )
        self.assertEqual(
            repair_order.invoice_id.invoice_line_ids[0].product_id.id,
            self.service_product.id,
            "The second invoice should only have 1 invoice line for the repair fee product."
        )
    
    def test_17_invoice_product_service_invoice_quantity(self):
        """
            Goals for test case 17 and test case 18:
                Creating invoice on 
                    + product with service policy is by quantity
                    + with/without log timesheet
                ==> does not make any change on the outcome
    
            Product:
                service_policy:      ordered_quantity
                service_tracking:    task_global_project (Create a task in an existing project)
    
            Input:
                Create repair order that has:
                    1 Repair Line
                    1 Repair Fee
                Add a log timesheet to the repair fee (corresponding task)
                Create an invoice for this repair order
            Expect:
                Successfully created an invoice
                invoice order line has data of both repair line and repair fee
                Total price of repair fee will be calculated according to the quantity
        """
    
        self.service_product.write({
            'service_policy': 'ordered_timesheet',
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        # Create repair order with repair fee of $50.0
        repair_order = self._create_repair_order(
            product_list=[self.service_product], 
            operations=True,
        )
    
        # Log Timesheet
        self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        # Create invoice
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.invoice_count, 1)
        self.assertTrue(bool(repair_order.invoice_id.invoice_line_ids[0].repair_line_ids))
        self.assertFalse(bool(repair_order.invoice_id.invoice_line_ids[1].repair_line_ids))
    
        self.assertFalse(bool(repair_order.invoice_id.invoice_line_ids[0].repair_fee_ids))
        self.assertTrue(bool(repair_order.invoice_id.invoice_line_ids[1].repair_fee_ids))
    
        self.assertFalse(bool(repair_order.invoice_id.invoice_line_ids[0].repair_fee_line_ids))
        self.assertTrue(bool(repair_order.invoice_id.invoice_line_ids[1].repair_fee_line_ids))
    
        repair_fee_product_price_unit = repair_order.invoice_id.invoice_line_ids[1].price_unit
        repair_fee_product_price_total = repair_order.invoice_id.invoice_line_ids[1].price_total
        quantity = repair_order.fees_lines.qty_invoiced
    
        self.assertEqual(
            repair_fee_product_price_unit * quantity,   # 50.0
            repair_fee_product_price_total,             # 50.0
            ("The price total should be calculated "
             "according to the quantity of the repair fee product.")
        )
    
    def test_18_invoice_product_service_invoice_quantity(self):
        """
            Goals for test case 17 and test case 18:
                Creating invoice on 
                    + product with service policy is by quantity
                    + with/without log timesheet
                ==> does not make any change on the outcome
    
            Product:
                service_policy:      ordered_quantity
                service_tracking:    task_global_project (Create a task in an existing project)
    
            Input:
                Create repair order that has:
                    1 Repair Line
                    1 Repair Fee
                Create an invoice for this repair order
            Expect:
                Successfully created an invoice
                invoice order line has data of both repair line and repair fee
                Total price of repair fee will be calculated according to the quantity
        """
    
        self.service_product.write({
            'service_policy': 'ordered_timesheet',
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        # Create repair order with repair fee of $50.0
        repair_order = self._create_repair_order(
            product_list=[self.service_product], 
            operations=True,
        )
    
        # Create invoice
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.invoice_count, 1)
        self.assertTrue(bool(repair_order.invoice_id.invoice_line_ids[0].repair_line_ids))
        self.assertFalse(bool(repair_order.invoice_id.invoice_line_ids[1].repair_line_ids))
    
        self.assertFalse(bool(repair_order.invoice_id.invoice_line_ids[0].repair_fee_ids))
        self.assertTrue(bool(repair_order.invoice_id.invoice_line_ids[1].repair_fee_ids))
    
        self.assertFalse(bool(repair_order.invoice_id.invoice_line_ids[0].repair_fee_line_ids))
        self.assertTrue(bool(repair_order.invoice_id.invoice_line_ids[1].repair_fee_line_ids))
    
        repair_fee_product_price_unit = repair_order.invoice_id.invoice_line_ids[1].price_unit
        repair_fee_product_price_total = repair_order.invoice_id.invoice_line_ids[1].price_total
        quantity = repair_order.fees_lines.qty_invoiced
    
        self.assertEqual(
            repair_fee_product_price_unit * quantity,   # 50.0
            repair_fee_product_price_total,             # 50.0
            ("The price total should be calculated "
             "according to the quantity of the repair fee product.")
        )
    
    def test_19_create_invoice_twice(self):
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product], True)
    
        # Log Timesheet
        self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.invoice_count, 1)
    
        with self.assertRaises(UserError):
            self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.invoice_count, 1)
    
    def test_20_create_invoice_twice_different_log_timesheet(self):
        """
            Product:
                'service_policy': 'delivered_timesheet'
                'service_tracking': 'task_global_project'
    
            Input:
                Create a repair order that has both 1 repair line and 1 repair fee
                Add log timesheet
                Create invoice
                Add log timesheet
                Create invoice
    
            Expect:
                Created 2 invoices in total
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product], True)
    
        # Log Timesheet fist time
        self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.invoice_count, 1)
    
        # Log Timesheet second time
        self._task_update_timesheet(
            name='Backup',
            task=repair_order.tasks_ids[0],
            time_start=9,
        )
    
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.invoice_count, 2)
    
    def test_21_create_invoice_twice_different_log_timesheet(self):
        """
            Product:
                'service_policy': 'ordered_timesheet' (based on quantity)
                'service_tracking': 'task_global_project'
    
            Input:
                Create a repair order that has both 1 repair line and 1 repair fee
                Add log timesheet
                Create invoice
                Add log timesheet
                Create invoice
    
            Expect:
                Create the second invoice is not possible
        """
    
        self.service_product.write({
            'service_policy': 'ordered_timesheet',
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
            'invoice_policy': 'order',
        })
    
        repair_order = self._create_repair_order([self.service_product], True)
    
        # Log Timesheet
        self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.invoice_count, 1)
    
        # Log Timesheet
        self._task_update_timesheet(
            name='Backup',
            task=repair_order.tasks_ids[0],
            time_start=10,
        )
    
        with self.assertRaises(UserError):
            self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.invoice_count, 1)
    
    def test_23_a_create_invoice_multi_repair_orders_no_particular_group(self):
        """
            Test creating invoice for multi repair orders
            Input:
                2 repair orders
                    Group = False
                    same partner
            Expect:
                1) 2 new invoices are created
                2) repair order A links to invoice 1
                    repair order 2 links to invoice 2
                    or vice versa
        """
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
        self.service_product_2.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order_1 = self._create_repair_order([self.service_product], True)
        repair_order_2 = self._create_repair_order([self.service_product], True)
    
        self.assertEqual(repair_order_1.partner_id.id, repair_order_2.partner_id.id)
    
        active_ro_ids = [repair_order_1.id, repair_order_2.id]
        ro_group = self.env['repair.order.make_invoice'].with_context({
            'active_ids': active_ro_ids
        }).create({'group': False})
        res = ro_group.make_invoices()
        new_invoice_ids = res['domain'][0][2]

        self.assertEqual(len(new_invoice_ids), 2)
        
        self.assertEqual(len(repair_order_1.invoice_ids), 1)
        self.assertEqual(len(repair_order_2.invoice_ids), 1)
        self.assertTrue(repair_order_1.invoice_ids.id in new_invoice_ids)
        self.assertTrue(repair_order_2.invoice_ids.id in new_invoice_ids)
        
        self.assertNotEqual(
            repair_order_1.invoice_ids.id,
            repair_order_2.invoice_ids.id
        )
        
        
    def test_23_b_create_invoice_multi_repair_orders_no_particular_group(self):
        """
            Test creating invoice for multi repair orders
            Input:
                2 repair orders
                    Group = False
                    different partners
            Expect:
                1) 2 new invoices are created
                2) repair order A links to invoice 1
                    repair order 2 links to invoice 2
                    or vice versa
        """
    
        repair_order_1 = self.env.ref('repair.repair_r1')
        repair_order_2 = self.env.ref('repair.repair_r0')
        repair_order_2.write({'partner_id': self.env.ref('base.res_partner_address_33').id})
    
        self.assertNotEqual(repair_order_1.partner_id.id, repair_order_2.partner_id.id)
    
        active_ro_ids = [repair_order_1.id, repair_order_2.id]
        ro_group = self.env['repair.order.make_invoice'].with_context({
            'active_ids': active_ro_ids
        }).create({'group': False})
        res = ro_group.make_invoices()
        new_invoice_ids = res['domain'][0][2]
        
        self.assertEqual(len(new_invoice_ids), 2, "There should be created 2 invoices in total.")
    
        self.assertEqual(len(repair_order_1.invoice_ids), 1)
        self.assertEqual(len(repair_order_2.invoice_ids), 1)
        self.assertTrue(repair_order_1.invoice_ids.id in new_invoice_ids)
        self.assertTrue(repair_order_2.invoice_ids.id in new_invoice_ids)
        
        self.assertNotEqual(
            repair_order_1.invoice_ids.id,
            repair_order_2.invoice_ids.id
        )
    
    def test_24_a_group_by_same_partner_and_currency(self):
        """
            Case:
                Create invoice for multi repair orders option "group" is selected
            Input:
                2 repair orders:
                    Group = True
                    same partner
            Expected Result:
                Create 1 invoice (invoice A) for both orders
                repair order 1 links to invoice A
                repair order 2 also links to invoice A
                repair_order_1.invoice_id == repair_order_2.invoice_id == invoice_A.id 
        """
    
        repair_order_1 = self.env.ref('repair.repair_r1')
        repair_order_2 = self.env.ref('repair.repair_r0')
    
        self.assertEqual(repair_order_1.partner_id.id, repair_order_2.partner_id.id)
    
        active_ro_ids = [repair_order_1.id, repair_order_2.id]
        ro_group = self.env['repair.order.make_invoice'].with_context({
            'active_ids': active_ro_ids
        }).create({'group': True})
        res = ro_group.make_invoices()
        new_invoice_ids = res['domain'][0][2]
    
        self.assertEqual(len(new_invoice_ids), 1)
    
        self.assertEqual(len(repair_order_1.invoice_ids), 1)
        self.assertEqual(len(repair_order_2.invoice_ids), 1)
        self.assertTrue(repair_order_1.invoice_ids.id in new_invoice_ids)
        self.assertTrue(repair_order_2.invoice_ids.id in new_invoice_ids)
        
        self.assertEqual(
            repair_order_1.invoice_ids.id,
            repair_order_2.invoice_ids.id,
            "Both order must link to the same invoice."
        )
    
    def test_24_b_group_by_same_partner_and_currency(self):
        """
            Test creating invoice for multi repair orders
            Input:
                2 repair orders
                    Group = True
                    different partners
            Expect:
                1) 2 new invoices are created
                2) repair order A links to invoice 1
                    repair order 2 links to invoice 2
                    or vice versa
        """
    
        repair_order_1 = self.env.ref('repair.repair_r1')
        repair_order_2 = self.env.ref('repair.repair_r0')
        repair_order_2.write({'partner_id': self.env.ref('base.res_partner_address_33').id})
    
        self.assertNotEqual(repair_order_1.partner_id.id, repair_order_2.partner_id.id)
    
        active_ro_ids = [repair_order_1.id, repair_order_2.id]
        ro_group = self.env['repair.order.make_invoice'].with_context({
            'active_ids': active_ro_ids
        }).create({'group': True})
        res = ro_group.make_invoices()
        new_invoice_ids = res['domain'][0][2]
    
        self.assertEqual(len(new_invoice_ids), 2)
    
        self.assertEqual(len(repair_order_1.invoice_ids), 1)
        self.assertEqual(len(repair_order_2.invoice_ids), 1)
        self.assertTrue(repair_order_1.invoice_ids.id in new_invoice_ids)
        self.assertTrue(repair_order_2.invoice_ids.id in new_invoice_ids)
        
        self.assertNotEqual(
            repair_order_1.invoice_ids.id,
            repair_order_2.invoice_ids.id
        )
    
    def test_27_edit_timesheet_task_no_created_invoice(self):
        """
            Repair fee product:
                ordered_timesheet:    timesheet
            Input:
                Create 1 repair order
                1) Log 1 timesheet
                2) Edit this timesheet
            Expect:
                1)     quantity delivered  = 1
                       quantity to invoice = 1
                2)     quantity delivered  = 2
                       quantity to invoice = 2
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        # Log Timesheet
        timesheet_line = self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        self.assertEqual(repair_order.fees_lines.qty_delivered, 1)
        self.assertEqual(repair_order.fees_lines.qty_to_invoice, 1)
    
        timesheet_line.write({'unit_amount': 2})
    
        self.assertEqual(repair_order.fees_lines.qty_delivered, 2)
        self.assertEqual(repair_order.fees_lines.qty_to_invoice, 2)
    
    def test_28_edit_timesheet_task_with_created_invoice(self):
        """
            Input:
                Create 1 repair order
                Log 1 timesheet
                Create 1 invoice
                Edit this timesheet
            Expect:
                Editing is not allowed
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        # Log Timesheet
        timesheet_line = self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        self._create_invoice(repair_order, 'delivered')
    
        with self.assertRaises(UserError):
            timesheet_line.write({'unit_amount': 2})
    
    def test_29_edit_timesheet_task_no_created_invoice(self):
        """
            Repair fee product:
                ordered_timesheet:    ordered quantity
            Input:
                Create 1 repair order
                1) Log 1 timesheet
                2) Edit this timesheet
            Expect:
                1)     quantity delivered  = 1
                       quantity to invoice = 1
                2)     quantity delivered  = 2
                       quantity to invoice = 1
        """
        self.service_product.write({
            'service_policy': 'ordered_timesheet',
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        # Log Timesheet
        timesheet_line = self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        self.assertEqual(repair_order.fees_lines.qty_delivered, 1)
        self.assertEqual(repair_order.fees_lines.qty_to_invoice, 1)
    
        timesheet_line.write({'unit_amount': 2})
    
        self.assertEqual(repair_order.fees_lines.qty_delivered, 2)
        self.assertEqual(repair_order.fees_lines.qty_to_invoice, 1)
    
    def test_30_edit_timesheet_task_created_invoice(self):
        """
            Repair fee product:
                ordered_timesheet:    ordered quantity
            Input:
                Create 1 repair order
                1) Log 1 timesheet
                2) Create invoice
                3) Edit this timesheet
            Expect:
                1)     quantity delivered  = 1
                       quantity to invoice = 1
                2)     quantity delivered  = 1
                       quantity to invoice = 0
                3)     quantity delivered  = 2
                       quantity to invoice = 0
        """
    
        self.service_product.write({
            'service_policy': 'ordered_timesheet',
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        # Log Timesheet
        timesheet_line = self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        self.assertEqual(repair_order.fees_lines.qty_delivered, 1)
        self.assertEqual(repair_order.fees_lines.qty_to_invoice, 1)
    
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.fees_lines.qty_delivered, 1)
        self.assertEqual(repair_order.fees_lines.qty_to_invoice, 0)
    
        timesheet_line.write({'unit_amount': 2})
    
        self.assertEqual(repair_order.fees_lines.qty_delivered, 2)
        self.assertEqual(repair_order.fees_lines.qty_to_invoice, 0)
    
    def test_31_unlink_timesheet_task_created_invoice(self):
        """
            Repair fee product:
                ordered_timesheet:    timesheet
            Input:
                Create 1 repair order
                1) Log 1 timesheet
                Create invoice
                2) unlink this timesheet
            Expect:
                Unlink is not allowed in this case
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        # Log Timesheet
        timesheet_line = self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        self.assertEqual(repair_order.fees_lines.qty_delivered, 1)
        self.assertEqual(repair_order.fees_lines.qty_to_invoice, 1)
    
        self._create_invoice(repair_order, 'delivered')
    
        self.assertEqual(repair_order.fees_lines.qty_delivered, 1)
        self.assertEqual(repair_order.fees_lines.qty_to_invoice, 0)
    
        with self.assertRaises(UserError):
            timesheet_line.unlink()
    
    def test_32_unlink_timesheet_task_no_invoice(self):
        """
            Repair fee product:
                ordered_timesheet:    timesheet
            Input:
                Create 1 repair order
                1) Log 1 timesheet
                2) unlink this timesheet
            Expect:
                Unlink successfully
                1)     quantity delivered  = 1
                       quantity to invoice = 1
                2)     quantity delivered  = 0
                       quantity to invoice = 0
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        # Log Timesheet
        timesheet_line = self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
        )
    
        self.assertEqual(repair_order.fees_lines.qty_delivered, 1)
        self.assertEqual(repair_order.fees_lines.qty_to_invoice, 1)
    
        timesheet_line.unlink()
    
        self.assertEqual(repair_order.fees_lines.qty_delivered, 0)
        self.assertEqual(repair_order.fees_lines.qty_to_invoice, 0)
    
    def test_33_manually_add_analytic_item(self):
        """
            Product 1:
                ordered_timesheet:    timesheet
            Product 2:
                expense policy: 'cost'
    
            Input:
                Create 1 repair order with 1 repair fee using product 1
                Manually create 1 more repair fee by accessing model 'account.analytic.line' that
                    uses the same analytic account as repair_order.analytic_acccount_id
    
            Expect:
                len(repair_order.fees_lines) == 2
        """
    
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'expense_policy': 'cost',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
        self.service_product_2.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'expense_policy': 'cost',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        self.assertEqual(len(repair_order.fees_lines), 1)
    
        # Log timesheet
        self.env['account.analytic.line'].create({
            'name': 'Extra service fee',
            'account_id': repair_order.analytic_account_id.id,
            'product_id': self.service_product_2.id,
            'project_id': repair_order.project_project_id.id,
            'date_start': '2021-09-20 08:00:00',
            'employee_id': self.env.ref('base.user_admin').employee_id.id,
            'time_start': 8,
            'unit_amount': 1,
        })
    
        self.assertEqual(len(repair_order.fees_lines), 2)
    
    def test_33_extra_1_manually_add_analytic_item(self):
        """
            Product 1:
                ordered_timesheet:    timesheet
            Product 2:
                expense policy: 'cost'
    
            Input:
                Create 1 repair order with 1 repair fee using product 1
                Manually create 1 more repair fee by accessing model 'account.analytic.line' that
                    uses the same analytic account as repair_order.analytic_acccount_id
    
            Expect:
                len(repair_order.fees_lines) == 2
        """
    
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'expense_policy': 'cost',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
        self.service_product_2.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'expense_policy': 'no',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        self.assertEqual(len(repair_order.fees_lines), 1)
    
        # Log timesheet
        self.env['account.analytic.line'].create({
            'name': 'Extra service fee',
            'account_id': repair_order.analytic_account_id.id,
            'product_id': self.service_product_2.id,
            'project_id': repair_order.project_project_id.id,
            'date_start': '2021-09-20 08:00:00',
            'employee_id': self.env.ref('base.user_admin').employee_id.id,
            'time_start': 8,
            'unit_amount': 1,
        })
    
        self.assertEqual(len(repair_order.fees_lines), 1)
    
    def test_33_extra_2_manually_add_analytic_item(self):
        """
            Product 1:
                ordered_timesheet:    timesheet
            Product 2:
                expense policy: 'cost'
    
            Input:
                Create 1 repair order with 1 repair fee using product 1
                Manually create 1 more repair fee by accessing model 'account.analytic.line' that
                    uses the same analytic account as repair_order.analytic_acccount_id
    
            Expect:
                len(repair_order.fees_lines) == 2
        """
    
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'project_only',
            'expense_policy': 'no',
        })
        self.service_product_2.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'expense_policy': 'cost',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        self.assertEqual(len(repair_order.fees_lines), 1)
    
        # Log timesheet
        self.env['account.analytic.line'].create({
            'name': 'Extra service fee',
            'account_id': repair_order.analytic_account_id.id,
            'product_id': self.service_product_2.id,
            'project_id': repair_order.project_project_id.id,
            'date_start': '2021-09-20 08:00:00',
            'employee_id': self.env.ref('base.user_admin').employee_id.id,
            'time_start': 8,
            'unit_amount': 1,
        })
    
        self.assertEqual(len(repair_order.fees_lines), 2)
    
    def test_33_extra_3_manually_add_analytic_item(self):
        """
            Product 1:
                ordered_timesheet:    timesheet
            Product 2:
                expense policy: 'cost'
    
            Input:
                Create 1 repair order with 1 repair fee using product 1
                Manually create 1 more repair fee by accessing model 'account.analytic.line' that
                    uses the same analytic account as repair_order.analytic_acccount_id
    
            Expect:
                len(repair_order.fees_lines) == 2
        """
    
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'project_only',
            'expense_policy': 'no',
        })
        self.service_product_2.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'project_only',
            'expense_policy': 'no',
        })
    
        repair_order = self._create_repair_order([self.service_product])
    
        self.assertEqual(len(repair_order.fees_lines), 1)
    
        # Log timesheet
        self.env['account.analytic.line'].create({
            'name': 'Extra service fee',
            'account_id': repair_order.analytic_account_id.id,
            'product_id': self.service_product_2.id,
            'project_id': repair_order.project_project_id.id,
            'date_start': '2021-09-20 08:00:00',
            'employee_id': self.env.ref('base.user_admin').employee_id.id,
            'time_start': 8,
            'unit_amount': 1,
        })
    
        self.assertEqual(len(repair_order.fees_lines), 1)
    
    def test_34_manually_add_analytic_item(self):
        """
            Manually add Analytic Item - add one more repair fee of a validated repair order
    
            Input:
                Create a repair order with a repair fee
                Confirm / validate it
                Create an analytic item that has:
                    + analytic account = repair_order.analytic_account_id
                    + product_id that has reinvoice_expense != 'no'
                        select the same product that is used to create repair order
                    + enter amount with negative value:
                        amount = price_unit (product_id.lst_price) * qty
                    + enter qty: the delivered amount,
                        here in this case = 1 (look at creation of repair order)
    
            Expect:
                No extra invoice is create, the total remains 1 repair fee
                field 'qty_delivered' of this existing repair fee is updated
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
            'expense_policy': 'sales_price',
        })
    
        repair_order = self.env['repair.order'].create({
            'product_id': self.product_to_repair.id,
            'product_uom': self.product_to_repair.uom_id.id,
            'product_qty': 1,
            'partner_id': self.partner_1.id,
            'create_invoice': True,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'user_id': self.env.uid,
            'company_id': self.env.company.id,
            'fees_lines': [
                (0, 0, {
                    'name': self.service_product.name,
                    'product_id': self.service_product.id,
                    'product_uom_qty': 1,
                    'product_uom': self.env.ref('uom.product_uom_unit').id,
                    'price_unit': self.service_product.lst_price, # 30.75
                    'tax_id': False
                })
            ]
        })
    
        repair_order.action_validate()
    
        self.assertEqual(len(repair_order.fees_lines), 1)
        self.assertEqual(repair_order.fees_lines.qty_delivered, 0)
        self.assertEqual(repair_order.fees_lines.qty_delivered, 0)
    
        self.env['account.analytic.line'].create({
            'name': 'Extra service fee',
            'account_id': repair_order.analytic_account_id.id,
            'product_id': self.service_product.id,
            'project_id': repair_order.project_project_id.id,
            'date_start': '2021-09-20 08:00:00',
            'employee_id': self.env.ref('base.user_admin').employee_id.id,
            'time_start': 8,
            'unit_amount': 1,
            # Manually enter the price, because:
            #    + Repair fee takes the Sales price of the product (price_unit)
            #    + Analytic item takes the Cost price of the product (amount)
            #    _repair_determine_order_line() use the amount to search for repair fee
            #     Thats why we must ensure the price_unit = amount
            # Calculation:
            #    amount = product.lst_price * timesheet.unit_mount * -1
            'amount': self.service_product.lst_price * 1 * -1,
        })
    
        self.assertEqual(len(repair_order.fees_lines), 1)
        self.assertEqual(repair_order.fees_lines.qty_delivered, 1)
        self.assertEqual(repair_order.fees_lines.qty_delivered, 1)
    
    def test_35_manually_add_analytic_item(self):
        """
            Manually add Analytic Item - add one more repair fee of a validated repair order
    
            Input:
                Create a repair order with a repair fee
                Only save the order WITHOUT confirm / validate it
    
                Create an analytic item. But because:
                    A repair order that has not been validated
                    will not generate an analytic_account_id
    
                Therefore, attempt to create an analytic item will raise an AssertionError
        """
    
        self.service_product.write({
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
            'expense_policy': 'sales_price',
        })
    
        # Create repair order
        repair_order = self.env['repair.order'].create({
            'product_id': self.product_to_repair.id,
            'product_uom': self.product_to_repair.uom_id.id,
            'product_qty': 1,
            'partner_id': self.partner_1.id,
            'create_invoice': True,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'user_id': self.env.uid,
            'company_id': self.env.company.id,
            'fees_lines': [
                (0, 0, {
                    'name': self.service_product.name,
                    'product_id': self.service_product.id,
                    'product_uom_qty': 1,
                    'product_uom': self.env.ref('uom.product_uom_unit').id,
                    'price_unit': 50,
                    'tax_id': False
                })
            ]
        })
    
        self.assertFalse(
            bool(repair_order.analytic_account_id),
            "There should be no analytic account created."
        )
