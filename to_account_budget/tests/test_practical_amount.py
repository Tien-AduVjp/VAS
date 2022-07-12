from unittest.mock import patch

from odoo import fields
from odoo.tests.common import Form, tagged

from .common import TestAccountBudgetCommon


@tagged('post_install', '-at_install')
class TestPracticalAmount(TestAccountBudgetCommon):
    def setUp(self):
        super(TestPracticalAmount, self).setUp()
        self.project_analytic_account = self.env['account.analytic.account'].create(
            {'name': 'project1_analytic_account'}
            )

        date_from = fields.Date.to_date('2021-01-01')
        date_to = fields.Date.to_date('2021-12-31')
        self.budget = self._create_crossovered_budget(date_from, date_to, posted_items_only=False)
        self.budget_line = self._create_crossovered_budget_line(
            self.budget,
            date_from,
            date_to,
            100000000,
            analytic_account=self.project_analytic_account)

    @patch('odoo.addons.to_account_budget.models.crossovered_budget_line.fields')
    def test_01_practical_amount_with_analytic_account(self, mock_obj):
        mock_obj.Date.today.return_value = fields.Date.to_date('2021-09-07')
        # Test: no use posted_items_only
        self._create_account_analytic_line(
            self.project_analytic_account,
            10000000,
            fields.Date.to_date('2021-05-05')
            )

        self._create_account_analytic_line(
            self.project_analytic_account,
            20000000,
            fields.Date.to_date('2020-05-05')
            )

        line1 = self._create_account_analytic_line(
            self.project_analytic_account,
            20000000,
            fields.Date.to_date('2021-05-05')
            )

        line2 = self._create_account_analytic_line(
            self.project_analytic_account,
            30000000,
            fields.Date.to_date('2021-02-02')
            )

        move1 = self._init_invoice('out_invoice',
                           price_unit=20000000,
                           invoice_date=fields.Date.to_date('2021-05-05'))

        move2 = self._init_invoice('out_invoice',
                           price_unit=30000000,
                           invoice_date=fields.Date.to_date('2021-02-02'))

        move2.action_post()

        line1.move_id = move1.line_ids[0]
        line2.move_id = move2.line_ids[0]

        self._init_invoice('out_invoice',
                           price_unit=30000000,
                           invoice_date=fields.Date.to_date('2021-02-02'),
                           analytic_account=self.project_analytic_account).action_post()
        self._init_invoice('out_invoice',
                           price_unit=40000000,
                           invoice_date=fields.Date.to_date('2021-02-06'),
                           analytic_account=self.project_analytic_account)
        self._init_invoice('out_invoice',
                           price_unit=50000000,
                           invoice_date=fields.Date.to_date('2020-02-02'),
                           analytic_account=self.project_analytic_account).action_post()
        self._init_invoice('out_invoice',
                           price_unit=60000000,
                           invoice_date=fields.Date.to_date('2020-02-06'),
                           analytic_account=self.project_analytic_account)
        self._init_invoice('out_invoice',
                           price_unit=70000000,
                           invoice_date=fields.Date.to_date('2021-02-02')).action_post()
        self._init_invoice('out_invoice',
                           price_unit=80000000,
                           invoice_date=fields.Date.to_date('2021-02-06'))

        self.assertEqual(self.budget_line.practical_amount, 90000000)
        self.assertEqual(self.budget_line.percentage, 1.314000000094608)

        # Test: use posted_items_only
        self.budget.posted_items_only = True
        self.budget_line.invalidate_cache()
        self.assertEqual(self.budget_line.practical_amount, 90000000)
        self.assertEqual(self.budget_line.percentage, 1.314000000094608)

    @patch('odoo.addons.to_account_budget.models.crossovered_budget_line.fields')
    def test_02_practical_amount_with_analytic_account_and_budgetary_position(self, mock_obj):
        mock_obj.Date.today.return_value = fields.Date.to_date('2021-09-07')

        self.budget.posted_items_only = True
        self.budget_line.general_budget_id = self.account_budget_post_sales0.id
        # Test: use posted_items_only
        self._create_account_analytic_line(
            self.project_analytic_account,
            10000000,
            fields.Date.to_date('2021-05-05')
            )

        line1 = self._create_account_analytic_line(
            self.project_analytic_account,
            20000000,
            fields.Date.to_date('2021-05-05')
            )

        line2 = self._create_account_analytic_line(
            self.project_analytic_account,
            20000000,
            fields.Date.to_date('2021-05-05')
            )

        move1 = self._init_invoice('out_invoice',
                           price_unit=20000000,
                           invoice_date=fields.Date.to_date('2021-05-05'),
                           account=self.account_revenue2)

        move2 = self._init_invoice('out_invoice',
                           price_unit=20000000,
                           invoice_date=fields.Date.to_date('2021-05-05'),
                           account=self.account_revenue2)
        move2.action_post()

        line1.move_id = move1.line_ids.filtered(lambda l: l.account_id == self.account_revenue2)
        line2.move_id = move2.line_ids.filtered(lambda l: l.account_id == self.account_revenue2)

        self._init_invoice('out_invoice',
                           price_unit=30000000,
                           invoice_date=fields.Date.to_date('2021-02-02'),
                           account=self.account_revenue).action_post()
        self._init_invoice('out_invoice',
                           price_unit=40000000,
                           invoice_date=fields.Date.to_date('2021-02-06'),
                           account=self.account_revenue2)

        self.assertEqual(self.budget_line.practical_amount, 20000000)
        self.assertEqual(self.budget_line.percentage, 0.29200000002102394)

        # Test: no use posted_items_only
        self.budget.posted_items_only = False
        self.budget_line.invalidate_cache()
        self.assertEqual(self.budget_line.practical_amount, 40000000)
        self.assertEqual(self.budget_line.percentage, 0.5840000000420479)

    @patch('odoo.addons.to_account_budget.models.crossovered_budget_line.fields')
    def test_03_practical_amount_without_analytic_account(self, mock_obj):
        mock_obj.Date.today.return_value = fields.Date.to_date('2021-09-07')
        # Test: without_analytic_account, with budgetary position and no use posted_items_only
        self.budget_line.write({'general_budget_id': self.account_budget_post_sales0.id,
                                'analytic_account_id': False,
                                })
        # Test: use posted_items_only
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
                           account=self.account_revenue).action_post()
        self._init_invoice('out_invoice',
                           price_unit=40000000,
                           invoice_date=fields.Date.to_date('2021-02-06'),
                           account=self.account_revenue2).action_post()
        self._init_invoice('out_invoice',
                           price_unit=50000000,
                           invoice_date=fields.Date.to_date('2020-02-02'),
                           account=self.account_revenue2).action_post()
        self._init_invoice('out_invoice',
                           price_unit=60000000,
                           invoice_date=fields.Date.to_date('2021-02-06'),
                           account=self.account_revenue2)

        self.assertEqual(self.budget_line.practical_amount, 110000000)
        self.assertEqual(self.budget_line.percentage, 1.6060000001156318)

        # Test: use posted_items_only
        self.budget.posted_items_only = True
        self.budget_line.invalidate_cache()
        self.assertEqual(self.budget_line.practical_amount, 40000000)
        self.assertEqual(self.budget_line.percentage, 0.5840000000420479)
