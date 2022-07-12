from odoo import fields
from odoo.tests.common import tagged

from odoo.addons.to_account_budget.tests.common import TestAccountBudgetCommon


@tagged('post_install', '-at_install')
class TestPracticalAmount(TestAccountBudgetCommon):
    def setUp(self):
        super(TestPracticalAmount, self).setUp()

        self.project_analytic_account = self.env['account.analytic.account'].create(
            {'name': 'project1_analytic_account'}
            )

        self.project1 = self.env['project.project'].create({
            'name': 'Project X',
            'allow_timesheets': True,
            'analytic_account_id': self.project_analytic_account.id,
        })
        self.task1 = self.env['project.task'].create({
            'name': 'Task One',
            'priority': '0',
            'kanban_state': 'normal',
            'project_id': self.project1.id,
        })

        self.employee = self.env['hr.employee'].create({
            'name': 'User Empl Employee',
            'user_id': self.env.user.id,
            'timesheet_cost': 100000,
        })

        date_from = fields.Date.to_date('2021-01-01')
        date_to = fields.Date.to_date('2021-12-31')
        self.budget = self._create_crossovered_budget(date_from, date_to, posted_items_only=False)

        self.budget_line = self._create_crossovered_budget_line(
            self.budget,
            date_from,
            date_to,
            100000000,
            analytic_account=self.project_analytic_account)

    def test_01_practical_amount_with_analytic_account_and_budgetary_position(self):
        self.budget_line.general_budget_id = self.account_budget_post_sales0
        # Test: no use posted_items_only and no use include_timesheets
        self.account_budget_post_sales0.include_timesheets = False

        self._create_account_analytic_line(
            self.project_analytic_account,
            20000000,
            fields.Date.to_date('2020-05-05')
            )

        line1 = self._create_account_analytic_line(
            self.project_analytic_account,
            10000000,
            fields.Date.to_date('2021-05-05')
            )

        move1 = self._init_invoice('out_invoice',
                           price_unit=10000000,
                           invoice_date=fields.Date.to_date('2021-05-05'),
                           account=self.account_revenue2)


        line1.move_id = move1.line_ids.filtered(lambda l: l.account_id == self.account_revenue2)

        self._init_invoice('out_invoice',
                           price_unit=30000000,
                           invoice_date=fields.Date.to_date('2021-02-02'),
                           analytic_account=self.project_analytic_account).post()
        self._init_invoice('out_invoice',
                           price_unit=40000000,
                           invoice_date=fields.Date.to_date('2021-02-06'),
                           analytic_account=self.project_analytic_account)
        self._init_invoice('out_invoice',
                           price_unit=50000000,
                           invoice_date=fields.Date.to_date('2020-02-02'),
                           analytic_account=self.project_analytic_account).post()
        self._init_invoice('out_invoice',
                           price_unit=60000000,
                           invoice_date=fields.Date.to_date('2020-02-06'),
                           analytic_account=self.project_analytic_account)

        # log some timesheet on task 1
        self._log_timesheet_on_task(unit_amount=4, date=fields.Date.to_date('2021-05-05'))
        self._log_timesheet_on_task(unit_amount=10, date=fields.Date.to_date('2020-05-05'))

        self.assertEqual(self.budget_line.practical_amount, 40000000)

        # Test: use include_timesheets and do not use posted_items_only
        self.budget_line.general_budget_id.update({'include_timesheets': True})
        self.budget_line.invalidate_cache()
        self.assertEqual(self.budget_line.practical_amount, 39600000)

    def test_02_practical_amount_with_analytic_account_and_budgetary_position(self):
        self.budget_line.general_budget_id = self.account_budget_post_sales0
        # Test: use posted_items_only and use include_timesheets
        self.budget.posted_items_only = True
        self.account_budget_post_sales0.include_timesheets = True

        line1 = self._create_account_analytic_line(
            self.project_analytic_account,
            10000000,
            fields.Date.to_date('2021-05-05')
            )

        move1 = self._init_invoice('out_invoice',
                           price_unit=10000000,
                           invoice_date=fields.Date.to_date('2021-05-05'),
                           account=self.account_revenue2)

        line1.move_id = move1.line_ids.filtered(lambda l: l.account_id == self.account_revenue2)

        self._log_timesheet_on_task(unit_amount=4, date=fields.Date.to_date('2021-05-05'))

        self.assertEqual(self.budget_line.practical_amount, 0)

    def _log_timesheet_on_task(self,
                               project=False,
                               task=False,
                               unit_amount=4,
                               date=fields.Date.today(),
                               employee=False):
        return self.env['account.analytic.line'].create({
            'project_id': project and project.id or self.project1.id,
            'task_id': task and task.id or self.task1.id,
            'name': 'timesheet for task %s' % (task or self.task1).name,
            'unit_amount': unit_amount,
            'date': date,
            'employee_id': employee and employee.id or self.employee.id
            })
