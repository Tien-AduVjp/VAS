from odoo.tests import TransactionCase, Form


class TestRepairTimesheetCommon(TransactionCase):
    def setUp(self):
        super().setUp()

        self.after_sales_services_project = self.env.ref('sale_timesheet.project_support')
        self.partner_1 = self.env.ref('base.res_partner_address_13')
        self.product_to_repair = self.env.ref('product.product_product_3')
        self.service_product = self.env.ref('repair.product_service_order_repair')
        self.service_product.write({'service_policy': 'delivered_timesheet'})
        self.service_product_2 = self.env.ref('sale_timesheet.product_service_order_timesheet')
        self.service_product_2.write({'service_policy': 'delivered_timesheet'})

    def _create_repair_order(self, product_list, operations=False, repair_line_product=False, bool_create_invoice=True):
        val_repair_order = {
            'product_id': self.product_to_repair.id,
            'product_uom': self.product_to_repair.uom_id.id,
            'product_qty': 1,
            'partner_id': self.partner_1.id,
            'create_invoice': bool_create_invoice,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'user_id': self.env.uid,
            'company_id': self.env.company.id,
        }

        # If operations is required then add repair line
        if operations:
            prod_id = repair_line_product.id if repair_line_product else self.env.ref('product.product_product_7').id
            prod_name = repair_line_product.id if repair_line_product else self.env.ref('product.product_product_7').name
            val_repair_order['operations'] = [
                (0, 0, {
                    'type': 'add',
                    'name': prod_name,
                    'product_id': prod_id,
                    'product_uom_qty': 5,
                    'product_uom': self.env.ref('uom.product_uom_unit').id,
                    'price_unit': 50,
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'src_location_id': self.env.ref('stock.stock_location_components').id,
                    'location_dest_id': self.env.ref('stock.stock_location_stock').id,
                    'tax_id': False,
                })
            ]

        # Add fee lines
        fee_lines = []
        for prod in product_list:
            fee_lines.append(
                (0, 0, {
                    'name': prod.name,
                    'product_id': prod.id,
                    'product_uom_qty': 1,
                    'product_uom': self.env.ref('uom.product_uom_unit').id,
                    'price_unit': 50,
                    'tax_id': False
                })
            )
        if fee_lines:
            val_repair_order['fees_lines'] = fee_lines

        # Finally create a repair order
        repair_order = self.env['repair.order'].with_context(tracking_disable=True).create(val_repair_order)

        ro_res = repair_order.action_validate()

        if not isinstance(ro_res, bool):
            self.assertRaises("Validating this order redirects to a wizard. "
                              "To-do: please handle this wizard")

        return repair_order

    def _create_invoice(self, repair_order, string_option):
        invoice = self.env['repair.advance.payment.inv'].create({
            'advance_payment_method': string_option
        })
        invoice.with_context({
            'active_id': repair_order.id,
            'active_ids': [repair_order.id]
        }).with_context(tracking_disable=True).create_invoices()

    def _task_update_timesheet(self, name, task, time_start, unit_amount=1):
        """
            Create a timesheet by calling Write on task
        """
        old_timesheet_ids = task.timesheet_ids.ids

        if time_start < 0 or time_start > 24:
            raise Exception('time start cannot be out of range from 0 to 23')

        repair_order = task.repair_fee_line_id.repair_id
        task.with_context(tracking_disable=True).write({
            'timesheet_ids': [
                (0, 0, {
                    'name': name,
                    'project_id': task.project_id.id,
                    'task_id': task.id,
                    'account_id': repair_order.analytic_account_id.id,
                    'date_start': '2021-09-20 %02d:00:00' % (time_start),
                    'employee_id': self.env.ref('base.user_admin').employee_id.id,
                    'time_start': time_start,
                    'unit_amount': unit_amount,
                })
            ]
        })

        # return timesheet_line that has just been created
        return task.timesheet_ids.filtered(lambda timesheet: timesheet.id not in old_timesheet_ids)
