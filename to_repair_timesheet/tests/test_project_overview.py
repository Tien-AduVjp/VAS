from odoo.tests import Form, tagged
from .common import TestRepairTimesheetCommon


@tagged('-at_install', 'post_install')
class TestProjectOverview(TestRepairTimesheetCommon):

    def _create_repair_order_for_ovewview(self):
        repair_order = self.env['repair.order'].with_context(tracking_disable=True).create({
            'product_id': self.product_to_repair.id,
            'product_uom': self.product_to_repair.uom_id.id,
            'product_qty': 1,
            'partner_id': self.partner_1.id,
            'create_invoice': True,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'user_id': self.env.uid,
            'company_id': self.env.company.id,
            'operations': [
                (0, 0, {
                    'type': 'add',
                    'name': self.env.ref('product.product_product_7').name,
                    'product_id': self.env.ref('product.product_product_7').id,
                    'product_uom_qty': 5,
                    'product_uom': self.env.ref('uom.product_uom_unit').id,
                    'price_unit': 50,
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'src_location_id': self.env.ref('stock.stock_location_components').id,
                    'location_dest_id': self.env.ref('stock.stock_location_stock').id,
                    'tax_id': False,
                })
            ],
            'fees_lines': [
                (0, 0, {
                    'name': self.service_product.name,
                    'product_id': self.service_product.id,
                    'product_uom_qty': 2,
                    'product_uom': self.env.ref('uom.product_uom_unit').id,
                    'price_unit': 50,
                    'tax_id': False
                }),
                (0, 0, {
                    'name': self.service_product.name,
                    'product_id': self.service_product.id,
                    'product_uom_qty': 2,
                    'product_uom': self.env.ref('uom.product_uom_unit').id,
                    'price_unit': 50,
                    'tax_id': False
                }),
            ]
        })

        ro_res = repair_order.action_validate()

        if not isinstance(ro_res, bool):
            self.assertRaises("Validating this order redirects to a wizard. "
                              "Please handle this wizard")

        return repair_order

    def test_36_multi_repair_fee_lines(self):
        """
            This test is checking on the price calculation
            with the below settings of the service product

            Input:
                1) Create a repair order with
                    1 repair line:
                        unit price = 50
                        quantity = 5
                    1 repair fee:
                        unit price = 50
                        quantity = 2
                        service policy = timesheet
                        service tracking = create task in an existed project
                    1 repair fee:
                        unit price = 50
                        quantity = 2
                        service policy = timesheet
                        service tracking = reate task in an existed project
                2) Log timesheet on task 1 and create invoice
                3) Post this invoice
                4) Log timesheet on task 2 and create invoice
                5) Post this invoice
            Expect:
                The price calculation is expected following the assertion test

            Note:
                Because the project is reused from the demo data and therefore
                contains some already culculated numbers.
                This is the answer to why the number are already this big just
                after creating the first repair order.
        """
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id
        })

        # Create repair order
        repair_order = self._create_repair_order_for_ovewview()

        computed_amounts_1 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_1['dashboard']['profit']['invoiced'], 0.0)
        self.assertEqual(computed_amounts_1['dashboard']['profit']['to_invoice'], 42500.0)
        self.assertEqual(computed_amounts_1['dashboard']['profit']['cost'], -2300.0)
        self.assertEqual(computed_amounts_1['dashboard']['profit']['total'], 40200.0)

        # Log timeshet on first task and
        self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
            unit_amount=2,
        )
        # create invoice
        self._create_invoice(repair_order, 'delivered')

        computed_amounts_2 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_2['dashboard']['profit']['invoiced'], 0.0)
        self.assertEqual(computed_amounts_2['dashboard']['profit']['to_invoice'], 42600.0)
        self.assertEqual(computed_amounts_2['dashboard']['profit']['cost'], -2500.0)
        self.assertEqual(computed_amounts_2['dashboard']['profit']['total'], 40100.0)

        # Post this invoice
        repair_order.invoice_ids[0].action_post()

        computed_amounts_3 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_3['dashboard']['profit']['invoiced'], 100.0)
        self.assertEqual(computed_amounts_3['dashboard']['profit']['to_invoice'], 42500.0)
        self.assertEqual(computed_amounts_3['dashboard']['profit']['cost'], -2500.0)
        self.assertEqual(computed_amounts_3['dashboard']['profit']['total'], 40100.0)

        # Log timesheet on second task and
        self._task_update_timesheet(
            name='Backup data',
            task=repair_order.tasks_ids[1],
            time_start=10,
            unit_amount=2,
        )
        # create invoice
        self._create_invoice(repair_order, 'delivered')

        computed_amounts_4 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_4['dashboard']['profit']['invoiced'], 100.0)
        self.assertEqual(computed_amounts_4['dashboard']['profit']['to_invoice'], 42600.0)
        self.assertEqual(computed_amounts_4['dashboard']['profit']['cost'], -2700.0)
        self.assertEqual(computed_amounts_4['dashboard']['profit']['total'], 40000.0)

        # Post the second invoice
        repair_order.invoice_ids[0].action_post()

        computed_amounts_5 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_5['dashboard']['profit']['invoiced'], 200.0)
        self.assertEqual(computed_amounts_5['dashboard']['profit']['to_invoice'], 42500.0)
        self.assertEqual(computed_amounts_5['dashboard']['profit']['cost'], -2700.0)
        self.assertEqual(computed_amounts_5['dashboard']['profit']['total'], 40000.0)

    def test_36_01_multi_repair_fee_lines(self):
        """
            This test is testing on the value assignment perspective
            closely following the previous input test on test 36

            Input:
                1) Create a repair order with
                    1 repair line:
                        unit price = 50
                        quantity = 5
                    1 repair fee:
                        unit price = 50
                        quantity = 2
                        service policy = timesheet
                        service tracking = create task in an existed project
                    1 repair fee:
                        unit price = 50
                        quantity = 2
                        service policy = timesheet
                        service tracking = create task in an existed project
                2) Log timesheet on task 1 and create invoice
                3) Log timesheet on task 2 and create invoice
            Expect:
                After first log timesheet:
                    1 invoice is created that consists of
                        1 invoice line for the repair line
                        1 invoice line for the invoiced repair fee, (feeA)
                        * The last repair fee remains uninvoiced
                After the second log timesheet:
                    1 invoice is created that consists of
                        1 invoice line for the rest repair fee (feeB)
                    the invoice on feeA != the invoice on feeB
                    the invoice line for feeA != invoice line for feeB
        """
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id
        })

        # Create repair order
        repair_order = self._create_repair_order_for_ovewview()

        self.assertEqual(len(repair_order.operations), 1, "Expect: repair order has 1 repair line.")
        self.assertEqual(len(repair_order.fees_lines), 2, "Expect: repair order has 2 repair fees.")

        # *********** LOG TIMESHEET ON FIRST TASK AND CREATE INVOICE ************* #
        self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
            unit_amount=2,
        )
        self._create_invoice(repair_order, 'delivered')

        # ******************************** #
        # ******** ASSERT TESTS 1 ******** #

        self.assertEqual(len(repair_order.invoice_ids), 1, "Expect: repair order has now 1 invoice in total.")

        invoice_1 = repair_order.invoice_ids[0]
        uninvoiced_repair_fee = repair_order.fees_lines.filtered(lambda f: not f.invoice_line_id)
        invoiced_repair_fee = repair_order.fees_lines.filtered(lambda f: f.invoice_line_id)

        # Test invoice level
        self.assertTrue(bool(uninvoiced_repair_fee), "Expect: 1 repair fee that isn't linked to any invoice line.")
        self.assertTrue(bool(invoiced_repair_fee), "Expect: 1 repair fee that is linked to an invoice line.")

        self.assertEqual(
            invoice_1.id,
            repair_order.operations[0].invoice_line_id.move_id.id,
            "Expect: Invoice on the repair order == invoice on the repair line."
        )
        self.assertEqual(
            invoice_1.id,
            invoiced_repair_fee.invoice_line_id.move_id.id,
            "Expect: invoice on the repair order == invoice on the invoiced repair fee."
        )

        # Test invoice line level
        invoice_line_for_repair_line = invoice_1.invoice_line_ids.filtered(lambda inv_line: inv_line.repair_line_ids.id == repair_order.operations.id)
        invoice_line_for_repair_fee = invoice_1.invoice_line_ids.filtered(lambda inv_line: inv_line.repair_fee_ids.id in repair_order.fees_lines.ids)

        self.assertEqual(
            len(invoice_1.invoice_line_ids),
            2,
            "Invoice 1 has now 2 invoice lines: 1 for repair line and 1 for repair fee."
        )
        self.assertEqual(
            len(repair_order.fees_lines.invoice_line_id),
            1,
            "Expect: there is only 1 invoiced repair fee among the total 2 repair fees."
        )
        self.assertEqual(
            len(repair_order.fees_lines.invoice_lines),
            1,
            "Expect: all repair fees has only 1 invoice line in total."
        )
        self.assertTrue(
            bool(invoice_line_for_repair_line),
            "Expect: Found an invoice line that is linked to the repair line."
        )
        self.assertTrue(
            bool(invoice_line_for_repair_fee),
            "Expect: Found an invoice line that is linked to the repair fee."
        )

        # *********** LOG TIMESHEET ON SECOND TASK AND CREATE INVOICE *************
        self._task_update_timesheet(
            name='Backup data',
            task=repair_order.tasks_ids[1],
            time_start=10,
            unit_amount=2,
        )
        self._create_invoice(repair_order, 'delivered')

        # ******************************** #
        # ******** ASSERT TESTS 2 ******** #

        self.assertEqual(
            len(repair_order.invoice_ids),
            2,
            "Expect: 2 invoices created in total after the second log timesheet."
        )
        self.assertEqual(
            len(repair_order.fees_lines.invoice_line_id),
            2,
            "Expect: there is 2 invoiced repair fee among the total 2 repair fees."
        )
        self.assertEqual(
            len(repair_order.fees_lines.invoice_lines),
            2,
            "Expect: all repair fees has now 2 invoice lines in total."
        )

        invoice_2 = repair_order.invoice_ids.filtered(lambda invoice: invoice.id != invoice_1.id)

        # First time log timesheet, both repair line and 1 of the 2 repair fees are invoiced
        self.assertEqual(len(invoice_1.invoice_line_ids.repair_line_ids), 1)
        self.assertEqual(len(invoice_1.invoice_line_ids.repair_fee_ids), 1)
        # Second time log timesheet, only the second repair fee is invoiced
        self.assertEqual(len(invoice_2.invoice_line_ids.repair_line_ids), 0)
        self.assertEqual(len(invoice_2.invoice_line_ids.repair_fee_ids), 1)

        repair_fee_has_invoice_1 = repair_order.fees_lines.filtered(lambda fee: fee.invoice_line_id.move_id.id == invoice_1.id)
        repair_fee_has_invoice_2 = repair_order.fees_lines.filtered(lambda fee: fee.invoice_line_id.move_id.id == invoice_2.id)

        self.assertNotEqual(invoice_1.id, invoice_2.id, "Expect: the 2 invoices are not identical.")
        self.assertEqual(
            len(repair_fee_has_invoice_1),
            1,
            "Expect: there found 1 repair fee that is linked to the invoice 1."
        )
        self.assertEqual(
            len(repair_fee_has_invoice_2),
            1,
            "Expect: there found 2 repair fee that is linked to the invoice 2."
        )
        self.assertNotEqual(
            repair_fee_has_invoice_1.id,
            repair_fee_has_invoice_2.id,
            "Expect: the 2 repair fees are linked to different invoices."
        )

        # TEST INVOICE LEVEL

        # Expect:
        #    The repair line is linked to invoice 1
        #    One of the repair fee is also linked to the invoice 1
        self.assertEqual(repair_order.operations[0].invoice_line_id.move_id.id, invoice_1.id)
        self.assertEqual(repair_fee_has_invoice_1.invoice_line_id.move_id.id, invoice_1.id)
        self.assertEqual(
            repair_order.operations[0].invoice_line_id.move_id.id,
            repair_fee_has_invoice_1.invoice_line_id.move_id.id
        )
        #    The second repair fee is linked to the invoice 2
        self.assertEqual(repair_fee_has_invoice_2.invoice_line_id.move_id.id, invoice_2.id)

        # TEST INVOICE LINE LEVEL
        self.assertEqual(len(invoice_2.invoice_line_ids), 1, "Expect: invoice 2 has only 1 invoice line.")
        self.assertEqual(
            len(invoice_2.invoice_line_ids.repair_fee_ids),
            1,
            "Expect: invoice 2 has 1 invoice line for the rest repair fee."
        )
        self.assertEqual(
            invoice_2.invoice_line_ids.repair_fee_ids[0].id,
            repair_fee_has_invoice_2.id
        )
        self.assertFalse(
            bool(invoice_2.invoice_line_ids.repair_line_ids),
            ("Expect: invoice 2 has no invoice line for the repair line, "
             "because this repair line has already been invoiced before.")
        )

    def test_37_multi_repair_fee_lines(self):
        """
            This test is checking on the price calculation
            with the below settings of the service product

            Input:
                1) Create a repair order with
                    1 repair line:
                        unit price = 50
                        quantity = 5
                    1 repair fee:
                        unit price = 50
                        quantity = 2
                        service policy = timesheet
                        service tracking = Create only project but not task
                    1 repair fee:
                        unit price = 50
                        quantity = 2
                        service policy = timesheet
                        service tracking = Create only project but not task
                2) Log timesheet on task 1 and create invoice
                3) Post this invoice
                4) Log timesheet on task 2 and create invoice
                5) Post this invoice
            Expect:
                The price calculation is expected following the assertion test

            Note:
                Because of the settings on the service product, a brandnew project is created
                with no task. It means all the 4 price numbers are expected to be 0 to start with
        """
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'project_only',
        })

        # Create repair order
        repair_order = self._create_repair_order_for_ovewview()

        self.env['project.task'].create({
            'name': 'Repair project task test',
            'project_id': repair_order.project_ids[0].id,
            'repair_fee_line_id': repair_order.fees_lines[0].id,
        })

        computed_amounts_1 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_1['dashboard']['profit']['invoiced'], 0.0)
        self.assertEqual(computed_amounts_1['dashboard']['profit']['to_invoice'], 0.0)
        self.assertEqual(computed_amounts_1['dashboard']['profit']['cost'], 0.0)
        self.assertEqual(computed_amounts_1['dashboard']['profit']['total'], 0.0)

        # Log Timesheet and
        self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
            unit_amount=2,
        )
        # Create invoice
        self._create_invoice(repair_order, 'delivered')

        self.assertEqual(len(repair_order.operations), 1)
        self.assertEqual(len(repair_order.fees_lines.invoice_line_id), 1)
        self.assertEqual(len(repair_order.fees_lines.invoice_lines), 1)

        computed_amounts_2 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_2['dashboard']['profit']['invoiced'], 0.0)
        self.assertEqual(computed_amounts_2['dashboard']['profit']['to_invoice'], 100.0)
        self.assertEqual(computed_amounts_2['dashboard']['profit']['cost'], -200.0)
        self.assertEqual(computed_amounts_2['dashboard']['profit']['total'], -100.0)

        repair_order.invoice_ids[0].action_post()

        computed_amounts_3 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_3['dashboard']['profit']['invoiced'], 100.0)
        self.assertEqual(computed_amounts_3['dashboard']['profit']['to_invoice'], 0.0)
        self.assertEqual(computed_amounts_3['dashboard']['profit']['cost'], -200.0)
        self.assertEqual(computed_amounts_3['dashboard']['profit']['total'], -100.0)

        # Log timesheet
        self._task_update_timesheet(
            name='Backup data',
            task=repair_order.tasks_ids[0],
            time_start=10,
            unit_amount=2,
        )
        # create invoice
        self._create_invoice(repair_order, 'delivered')

        self.assertEqual(len(repair_order.operations), 1)
        self.assertEqual(len(repair_order.fees_lines.invoice_line_id), 1)
        self.assertEqual(len(repair_order.fees_lines.invoice_lines), 2)

        computed_amounts_4 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_4['dashboard']['profit']['invoiced'], 100.0)
        self.assertEqual(computed_amounts_4['dashboard']['profit']['to_invoice'], 100.0)
        self.assertEqual(computed_amounts_4['dashboard']['profit']['cost'], -400.0)
        self.assertEqual(computed_amounts_4['dashboard']['profit']['total'], -200.0)

        repair_order.invoice_ids[1].action_post()

        computed_amounts_5 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_5['dashboard']['profit']['invoiced'], 200.0)
        self.assertEqual(computed_amounts_5['dashboard']['profit']['to_invoice'], 0.0)
        self.assertEqual(computed_amounts_5['dashboard']['profit']['cost'], -400.0)
        self.assertEqual(computed_amounts_5['dashboard']['profit']['total'], -200.0)

    def test_38_multi_repair_fee_lines(self):
        """
            This test is checking on the price calculation
            with the below settings of the service product

            Input:
                1) Create a repair order with
                    1 repair line:
                        unit price = 50
                        quantity = 5
                    1 repair fee:
                        unit price = 50
                        quantity = 2
                        service policy = timesheet
                        service tracking = create task in an existed project
                    1 repair fee:
                        unit price = 50
                        quantity = 2
                        service policy = timesheet
                        service tracking = create task in an existed project
                2) Log timesheet on both task 1 and task 2 and create invoice
                3) Post this invoice
                4) Log timesheet on task 2 and create invoice
                5) Post this invoice
            Expect:
                The price calculation is expected following the assertion test

            Note:
                Because the project is reused from the demo data and therefore
                contains some already culculated numbers.
                This is the answer to why the number are already this big just
                after creating the first repair order.
        """
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id
        })

        # Create and Confirm repair order with 2 repair lines <==> 2 tasks
        repair_order = self._create_repair_order_for_ovewview()

        computed_amounts_1 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_1['dashboard']['profit']['invoiced'], 0.0)
        self.assertEqual(computed_amounts_1['dashboard']['profit']['to_invoice'], 42500)
        self.assertEqual(computed_amounts_1['dashboard']['profit']['cost'], -2300)
        self.assertEqual(computed_amounts_1['dashboard']['profit']['total'], 40200)

        # Log Timesheet
        self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
            unit_amount=2,
        )
        self._task_update_timesheet(
            name='Clean up data',
            task=repair_order.tasks_ids[1],
            time_start=10,
            unit_amount=2,
        )
        # Create invoice
        self._create_invoice(repair_order, 'delivered')

        self.assertEqual(len(repair_order.operations), 1)
        self.assertEqual(len(repair_order.fees_lines.invoice_line_id), 2)
        self.assertEqual(len(repair_order.fees_lines.invoice_lines), 2)

        computed_amounts_2 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_2['dashboard']['profit']['invoiced'], 0.0)
        self.assertEqual(computed_amounts_2['dashboard']['profit']['to_invoice'], 42700.0)
        self.assertEqual(computed_amounts_2['dashboard']['profit']['cost'], -2700.0)
        self.assertEqual(computed_amounts_2['dashboard']['profit']['total'], 40000.0)

        # Post the invoice
        repair_order.invoice_ids[0].action_post()

        computed_amounts_3 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_3['dashboard']['profit']['invoiced'], 200.0)
        self.assertEqual(computed_amounts_3['dashboard']['profit']['to_invoice'], 42500.0)
        self.assertEqual(computed_amounts_3['dashboard']['profit']['cost'], -2700.0)
        self.assertEqual(computed_amounts_3['dashboard']['profit']['total'], 40000.0)

        # Log timesheet on second task and create invoice
        self._task_update_timesheet(
            name='Backup data',
            task=repair_order.tasks_ids[1],
            time_start=10,
            unit_amount=2,
        )
        self._create_invoice(repair_order, 'delivered')

        self.assertEqual(len(repair_order.operations), 1)
        self.assertEqual(len(repair_order.fees_lines.invoice_line_id), 2)
        self.assertEqual(len(repair_order.fees_lines.invoice_lines), 3)

        computed_amounts_4 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_4['dashboard']['profit']['invoiced'], 200.0)
        self.assertEqual(computed_amounts_4['dashboard']['profit']['to_invoice'], 42600.0)
        self.assertEqual(computed_amounts_4['dashboard']['profit']['cost'], -2900.0)
        self.assertEqual(computed_amounts_4['dashboard']['profit']['total'], 39900.0)

        # Post the second invoice
        repair_order.invoice_ids[1].action_post()

        computed_amounts_5 = repair_order.project_ids[0]._plan_prepare_values()

        self.assertEqual(computed_amounts_5['dashboard']['profit']['invoiced'], 300.0)
        self.assertEqual(computed_amounts_5['dashboard']['profit']['to_invoice'], 42500.0)
        self.assertEqual(computed_amounts_5['dashboard']['profit']['cost'], -2900.0)
        self.assertEqual(computed_amounts_5['dashboard']['profit']['total'], 39900.0)

    def test_38_01_multi_repair_fee_lines(self):
        """
            Input:
                1) Create a repair order with
                    1 repair line:
                        unit price = 50
                        quantity = 5
                    1 repair fee:
                        unit price = 50
                        quantity = 2
                        service policy = timesheet
                        service tracking = create task in an existed project
                    1 repair fee:
                        unit price = 50
                        quantity = 2
                        service policy = timesheet
                        service tracking = create task in an existed project
                2) Log timesheet on both task 1 and task 2 and create invoice
                3) Log timesheet on task 2 and create invoice
            Expect:
                After first log timesheet:
                    1 invoice is created that consists of
                        1 invoice line for the repair line
                        1 invoice line for the repair fee 1, (feeA)
                        1 invoice line for the repair fee 2, (feeB)
                        ==> 3 invoice lines in total
                After the second log timesheet:
                    1 invoice is created that consists of
                        1 invoice line for the rest repair fee (feeB)
                    the invoice on feeA != the invoice on feeB
                    the invoice line for feeA != invoice line for feeB
        """
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('sale_timesheet.project_support').id
        })

        # Create and Confirm repair order with 2 repair lines <==> 2 tasks
        repair_order = self._create_repair_order_for_ovewview()

        self.assertEqual(len(repair_order.operations), 1)
        self.assertEqual(len(repair_order.fees_lines), 2)

        # *********** FIRST TIME: LOG TIMESHEET ON BOTH TASK AND CREATE INVOICE ************* #
        self._task_update_timesheet(
            name='Preparation Fix',
            task=repair_order.tasks_ids[0],
            time_start=8,
            unit_amount=2,
        )
        self._task_update_timesheet(
            name='Cleanup data',
            task=repair_order.tasks_ids[1],
            time_start=10,
            unit_amount=2,
        )
        self._create_invoice(repair_order, 'delivered')

        # ******************************** #
        # ******** ASSERT TESTS 1 ******** #

        self.assertEqual(len(repair_order.invoice_ids), 1, "Expect: repair order has now 1 invoice in total.")

        invoice_1 = repair_order.invoice_ids[0]

        self.assertEqual(
            len(invoice_1.invoice_line_ids),
            3,
            "Expect 3 invoices line created."
        )
        self.assertEqual(
            len(repair_order.fees_lines.invoice_line_id),
            2,
            "Expect: there is 2 invoiced repair fee among the total 2 repair fees."
        )
        self.assertEqual(
            len(repair_order.fees_lines.invoice_lines),
            2,
            "Expect: all repair fees has 2 invoice lines in total."
        )

        invoice_1_lines = invoice_1.invoice_line_ids
        invoice_line_for_repair_line = invoice_1_lines.filtered(lambda inv_line: inv_line.repair_line_ids.id == repair_order.operations.id)
        invoice_line_for_repair_fee_1 = invoice_1_lines.filtered(lambda inv_line: inv_line.repair_fee_ids.id == repair_order.fees_lines[0].id)
        invoice_line_for_repair_fee_2 = invoice_1_lines.filtered(lambda inv_line: inv_line.repair_fee_ids.id == repair_order.fees_lines[1].id)

        self.assertTrue(bool(repair_order.operations[0].invoice_line_id.move_id), "Expect: the repair line is invoiced")
        self.assertTrue(bool(invoice_line_for_repair_line), "Expect: the repair line is linked to an invoice line.")
        self.assertTrue(bool(invoice_line_for_repair_fee_1), "Expect: the repair fee 1 is linked to an invoice line.")
        self.assertTrue(bool(invoice_line_for_repair_fee_2), "Expect: the repair fee 2 is linked to an invoice line.")
        self.assertNotEqual(
            invoice_line_for_repair_fee_1,
            invoice_line_for_repair_fee_2,
            "Expect: the 2 repair fees are not linked to the same invoice line."
        )

        # Expect: invoice on repair order == invoice on repair line = invoice on repair fee 1 & 2
        self.assertEqual(
            invoice_1.id,
            repair_order.operations[0].invoice_line_id.move_id.id,
            "Expect: Invoice on the repair order == invoice on the repair line."
        )
        self.assertEqual(
            invoice_1.id,
            repair_order.fees_lines[0].invoice_line_id.move_id.id,
            "Expect: invoice on the repair order == invoice on the invoiced repair fee 1."
        )
        self.assertEqual(
            invoice_1.id,
            repair_order.fees_lines[1].invoice_line_id.move_id.id,
            "Expect: invoice on the repair order == invoice on the invoiced repair fee 2."
        )
        self.assertEqual(
            repair_order.operations[0].invoice_line_id.move_id.id,
            repair_order.fees_lines[0].invoice_line_id.move_id.id
        )
        self.assertEqual(
            repair_order.operations[0].invoice_line_id.move_id.id,
            repair_order.fees_lines[1].invoice_line_id.move_id.id
        )
        self.assertEqual(
            repair_order.fees_lines[0].invoice_line_id.move_id.id,
            repair_order.fees_lines[1].invoice_line_id.move_id.id
        )

        # *********** LOG TIMESHEET ON SECOND TASK AND CREATE INVOICE *************
        self._task_update_timesheet(
            name='Backup data',
            task=repair_order.tasks_ids[1],
            time_start=10,
            unit_amount=2,
        )
        self._create_invoice(repair_order, 'delivered')

        # ******************************** #
        # ******** ASSERT TESTS 2 ******** #

        self.assertEqual(
            len(repair_order.invoice_ids),
            2,
            "Expect: 2 invoices created in total after the second log timesheet."
        )
        self.assertEqual(
            len(repair_order.fees_lines.invoice_line_id),
            2,
            "Expect: there is 2 invoiced repair fee among the total 2 repair fees."
        )
        self.assertEqual(
            len(repair_order.fees_lines.invoice_lines),
            3,
            "Expect: all repair fees has now 3 invoice lines in total."
        )

        invoice_2 = repair_order.invoice_ids.filtered(lambda invoice: invoice.id != invoice_1.id)

        # First time log timesheet, both repair line and 1 of the 2 repair fees are invoiced
        self.assertEqual(len(invoice_1.invoice_line_ids.repair_line_ids), 1)
        self.assertEqual(len(invoice_1.invoice_line_ids.repair_fee_line_ids), 2)
        # Second time log timesheet, only the second repair fee is invoiced
        self.assertEqual(len(invoice_2.invoice_line_ids.repair_line_ids), 0)
        self.assertEqual(len(invoice_2.invoice_line_ids.repair_fee_line_ids), 1)

        self.assertEqual(len(invoice_2.invoice_line_ids), 1, "This invoice only has 1 invoice line")
        self.assertFalse(
            bool(invoice_2.invoice_line_ids.repair_line_ids),
            ("Expect: invoice 2 has no invoice line for the repair line, "
             "because this repair line has already been invoiced before.")
        )
        self.assertFalse(
            repair_order.fees_lines[0].invoice_lines & repair_order.fees_lines[1].invoice_lines,
            "Expect: the 2 repair fees are not linked to the same invoice line."
        )
        repair_fee_has_invoice_2 = repair_order.fees_lines.filtered(lambda fee: len(fee.invoice_lines) == 2)

        self.assertTrue(repair_fee_has_invoice_2, "Expect: the second repair fee is linked to 2 invoice lines.")

        repair_fee_2_invoice_1 = repair_fee_has_invoice_2.invoice_lines.filtered(lambda i: i.move_id.id == invoice_1.id)
        repair_fee_2_invoice_2 = repair_fee_has_invoice_2.invoice_lines.filtered(lambda i: i.move_id.id == invoice_2.id)
        self.assertTrue(bool(repair_fee_2_invoice_1))
        self.assertTrue(bool(repair_fee_2_invoice_2))
        self.assertNotEqual(
            repair_fee_2_invoice_1,
            repair_fee_2_invoice_2,
            "Expect: the second repair fee is linked to 2 different invoices."
        )
