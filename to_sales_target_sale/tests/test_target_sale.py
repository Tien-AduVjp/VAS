from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from odoo.tests import tagged
from odoo import fields

from .common import TestTargetSaleCommon
from unittest.mock import patch


@tagged('post_install', '-at_install')
class TestTargetSale(TestTargetSaleCommon):

    @patch.object(fields.Datetime, 'now', lambda: fields.Datetime.to_datetime('2019-09-09 09:00:00'))
    def setUp(self):
        super(TestTargetSale, self).setUp()

        self.so = self.create_so(self.product_sale, user_create=self.user_salesman)

        self.sale_target = self.form_create_team_target(self.team1,
                                               fields.Datetime.now(),
                                               fields.Datetime.now() + timedelta(days=31),
                                               target=160000)

        self.sale_target_saleman = self.sale_target.personal_target_ids.filtered(lambda r: r.sale_person_id == self.user_salesman)
        self.sale_target_saleman.target = 100000
        self.sale_target_leader = self.sale_target.personal_target_ids - self.sale_target_saleman
        self.sale_target_leader.target = 60000

        self.sale_target.action_confirm()
        self.sale_target.action_approve()

    @patch.object(fields.Datetime, 'now', lambda: fields.Datetime.to_datetime('2019-09-09 09:00:00'))
    def test_linking_so_invoice_to_target(self):
        # Test SO linking to Sale team's target
        # Export Invoice from SO
        invoice_exported = self.create_posted_invoice_from_so(self.so)

        # Create new team target invalid
        sale_target_outrange_date = self.form_create_team_target_approve(self.team1,
                               fields.Datetime.now() + timedelta(days=32),
                               fields.Datetime.now() + timedelta(days=35),
                               target=10000)

        # Get personal target invalid
        sale_target_saleman_outrange_date = sale_target_outrange_date.personal_target_ids.filtered(lambda r: r.sale_person_id == self.user_salesman)

        empty_invoice = self.env['account.move']
        # The sales target date is out range with the date on the SO.
        self.assertEqual(sale_target_outrange_date.sale_order_ids, self.SaleOrder, "SO valid is not linked to Sales team's target!")
        self.assertEqual(sale_target_outrange_date.sale_orders_count, 0, "Count SO displayed in view Sales target is incorrect!")
        self.assertEqual(sale_target_saleman_outrange_date.sale_order_ids, self.SaleOrder, "SO valid is not linked to Sales team's target!")
        self.assertEqual(sale_target_saleman_outrange_date.sale_orders_count, 0, "Count SO displayed in view Sales target is incorrect!")

        self.assertEqual(sale_target_outrange_date.sales_invoice_ids, empty_invoice, "Invoice valid is not linked to Sales team's target!")
        self.assertEqual(sale_target_outrange_date.sales_invoices_count, 0, "Count Invoice displayed in view Sales target is incorrect!")
        self.assertEqual(sale_target_saleman_outrange_date.sales_invoice_ids, empty_invoice, "Invoice valid is not linked to Sales team's target!")
        self.assertEqual(sale_target_saleman_outrange_date.sales_invoices_count, 0, "Count Invoice displayed in view Sales target is incorrect!")

        # The sales target date within the date on the SO.
        self.assertEqual(self.sale_target.sale_order_ids, self.so, "SO valid is not linked to Sales team's target!")
        self.assertEqual(self.sale_target.sale_orders_count, 1, "Count SO displayed in view Sales target is incorrect!")
        self.assertEqual(self.sale_target_saleman.sale_order_ids, self.so, "SO valid is not linked to Sales team's target!")
        self.assertEqual(self.sale_target_saleman.sale_orders_count, 1, "Count SO displayed in view Sales target is incorrect!")

        self.assertEqual(self.sale_target.sales_invoice_ids, invoice_exported, "Invoice valid is not linked to Sales team's target!")
        self.assertEqual(self.sale_target.sales_invoices_count, 1, "Count Invoice displayed in view Sales target is incorrect!")
        self.assertEqual(self.sale_target_saleman.sales_invoice_ids, invoice_exported, "Invoice valid is not linked to Sales team's target!")
        self.assertEqual(self.sale_target_saleman.sales_invoices_count, 1, "Count Invoice displayed in view Sales target is incorrect!")

    @patch.object(fields.Datetime, 'now', lambda: fields.Datetime.to_datetime('2019-09-09 09:00:00'))
    def test_compute_sales_kpi_on_target(self):
        team_target = self.sale_target.target
        saleman_target = self.sale_target_saleman.target
        leader_target = self.sale_target_leader.target
        value_salesman = 10000  # SO value 10000

        # Team target just have had 1 SO belongs user salesman (no invoiced)
        self.assertEqual(self.sale_target.untaxed_sales_total, value_salesman)
        self.assertEqual(self.sale_target.sales_target_reached, value_salesman * 100 / team_target)
        self.assertEqual(self.sale_target.sales_invoiced, 0)
        self.assertEqual(self.sale_target.invoiced_target_reached, 0)
        self.assertEqual(self.sale_target.sales_total, 0)
        self.assertEqual(self.sale_target.target_reached, 0)

        self.assertEqual(self.sale_target_saleman.untaxed_sales_total, value_salesman)
        self.assertEqual(self.sale_target_saleman.sales_target_reached, value_salesman * 100 / saleman_target)
        self.assertEqual(self.sale_target_saleman.sales_invoiced, 0)
        self.assertEqual(self.sale_target_saleman.invoiced_target_reached, 0)
        self.assertEqual(self.sale_target_saleman.sales_total, 0)
        self.assertEqual(self.sale_target_saleman.target_reached, 0)

        self.assertEqual(self.sale_target_leader.untaxed_sales_total, 0)
        self.assertEqual(self.sale_target_leader.sales_target_reached, 0)
        self.assertEqual(self.sale_target_leader.sales_invoiced, 0)
        self.assertEqual(self.sale_target_leader.invoiced_target_reached, 0)
        self.assertEqual(self.sale_target_leader.sales_total, 0)
        self.assertEqual(self.sale_target_leader.target_reached, 0)

        # user_leader create new SO and post invoiced it
        so_leader = self.create_so(self.product_sale, qty=7, user_create=self.user_leader)
        posted_leader_invoice = self.create_posted_invoice_from_so(so_leader)
        value_leader = 35000  # SO value: 35000
        total_value = value_leader + value_salesman

        self.assertEqual(self.sale_target.untaxed_sales_total, total_value)
        self.assertEqual(self.sale_target.sales_target_reached, total_value * 100 / team_target)
        self.assertEqual(self.sale_target.sales_invoiced, value_leader)
        self.assertEqual(self.sale_target.invoiced_target_reached, value_leader * 100 / team_target)
        self.assertEqual(self.sale_target.sales_total, value_leader)
        self.assertEqual(self.sale_target.target_reached, 35000 * 100 / team_target)

        self.assertEqual(self.sale_target_saleman.untaxed_sales_total, value_salesman)
        self.assertEqual(self.sale_target_saleman.sales_target_reached, value_salesman * 100 / saleman_target)
        self.assertEqual(self.sale_target_saleman.sales_invoiced, 0)
        self.assertEqual(self.sale_target_saleman.invoiced_target_reached, 0)
        self.assertEqual(self.sale_target_saleman.sales_total, 0)
        self.assertEqual(self.sale_target_saleman.target_reached, 0)

        self.assertEqual(self.sale_target_leader.untaxed_sales_total, value_leader)
        self.assertEqual(self.sale_target_leader.sales_target_reached, value_leader * 100 / leader_target)
        self.assertEqual(self.sale_target_leader.sales_invoiced, value_leader)
        self.assertEqual(self.sale_target_leader.invoiced_target_reached, value_leader * 100 / leader_target)
        self.assertEqual(self.sale_target_leader.sales_total, value_leader)
        self.assertEqual(self.sale_target_leader.target_reached, value_leader * 100 / leader_target)

        # First SO belonging salesman is invoiced and post
        self.create_posted_invoice_from_so(self.so)

        self.assertEqual(self.sale_target.untaxed_sales_total, total_value)
        self.assertEqual(self.sale_target.sales_target_reached, total_value * 100 / team_target)
        self.assertEqual(self.sale_target.sales_invoiced, total_value)
        self.assertEqual(self.sale_target.invoiced_target_reached, total_value * 100 / team_target)
        self.assertEqual(self.sale_target.sales_total, total_value)
        self.assertEqual(self.sale_target.target_reached, total_value * 100 / team_target)

        self.assertEqual(self.sale_target_saleman.untaxed_sales_total, value_salesman)
        self.assertEqual(self.sale_target_saleman.sales_target_reached, value_salesman * 100 / saleman_target)
        self.assertEqual(self.sale_target_saleman.sales_invoiced, value_salesman)
        self.assertEqual(self.sale_target_saleman.invoiced_target_reached, value_salesman * 100 / saleman_target)
        self.assertEqual(self.sale_target_saleman.sales_total, value_salesman)
        self.assertEqual(self.sale_target_saleman.target_reached, value_salesman * 100 / saleman_target)

        self.assertEqual(self.sale_target_leader.untaxed_sales_total, value_leader)
        self.assertEqual(self.sale_target_leader.sales_target_reached, value_leader * 100 / leader_target)
        self.assertEqual(self.sale_target_leader.sales_invoiced, value_leader)
        self.assertEqual(self.sale_target_leader.invoiced_target_reached, value_leader * 100 / leader_target)
        self.assertEqual(self.sale_target_leader.sales_total, value_leader)
        self.assertEqual(self.sale_target_leader.target_reached, value_leader * 100 / leader_target)

        # Cancel SO and Invoice of leader
        so_leader.action_cancel()
        posted_leader_invoice.button_draft()

        self.assertEqual(self.sale_target.untaxed_sales_total, value_salesman)
        self.assertEqual(self.sale_target.sales_target_reached, value_salesman * 100 / team_target)
        self.assertEqual(self.sale_target.sales_invoiced, value_salesman)
        self.assertEqual(self.sale_target.invoiced_target_reached, value_salesman * 100 / team_target)
        self.assertEqual(self.sale_target.sales_total, value_salesman)
        self.assertEqual(self.sale_target.target_reached, value_salesman * 100 / team_target)

        self.assertEqual(self.sale_target_saleman.untaxed_sales_total, value_salesman)
        self.assertEqual(self.sale_target_saleman.sales_target_reached, value_salesman * 100 / saleman_target)
        self.assertEqual(self.sale_target_saleman.sales_invoiced, value_salesman)
        self.assertEqual(self.sale_target_saleman.invoiced_target_reached, value_salesman * 100 / saleman_target)
        self.assertEqual(self.sale_target_saleman.sales_total, value_salesman)
        self.assertEqual(self.sale_target_saleman.target_reached, value_salesman * 100 / saleman_target)

        self.assertEqual(self.sale_target_leader.untaxed_sales_total, 0)
        self.assertEqual(self.sale_target_leader.sales_target_reached, 0)
        self.assertEqual(self.sale_target_leader.sales_invoiced, 0)
        self.assertEqual(self.sale_target_leader.invoiced_target_reached, 0)
        self.assertEqual(self.sale_target_leader.sales_total, 0)
        self.assertEqual(self.sale_target_leader.target_reached, 0)

    @patch.object(fields.Date, 'today', lambda: fields.Datetime.to_datetime('2018-09-09'))
    def test_cron_update_current_month_target(self):
        today = fields.Date.today()
        month_end_date = (date(today.year, today.month, 1) + relativedelta(months=1) + timedelta(days=-1))

        # Create target team1
        target_team1 = self.form_create_team_target(self.team1,
                                   today,
                                   today + timedelta(days=31),
                                   target=160000)
        self.sale_target_saleman = target_team1.personal_target_ids.filtered(lambda r: r.sale_person_id == self.user_salesman)
        self.sale_target_saleman.target = 100000
        target_team1.action_confirm()
        target_team1.action_approve()

        # Create target team2 to check singleton when run cron
        target_team2 = self.form_create_team_target(self.team2,
                                   today,
                                   today + timedelta(days=31),
                                   target=100000)
        target_team2.action_confirm()
        target_team2.action_approve()

        self.env.ref('to_sales_target_sale.cron_compute_crm_team_current_month_invoiced_target').method_direct_trigger()
        self.env.ref('to_sales_target_sale.cron_compute_res_user_current_month_target_sales_invoiced').method_direct_trigger()

        total_days_in_month_target_team1 = (month_end_date - target_team1.start_date).days + 1
        target_month_team = total_days_in_month_target_team1 * 5000  # Average per day: target / (start_date - end_date)
        target_month_salesman = total_days_in_month_target_team1 * 3125

        self.assertEqual(self.team1.invoiced_target, target_month_team, "cron_compute_crm_team_current_month_invoiced_target run wrong")
        self.assertEqual(self.user_salesman.target_sales_invoiced, target_month_salesman, "cron_compute_res_user_current_month_target_sales_invoiced run wrong")
