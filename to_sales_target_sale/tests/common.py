from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.tests import Form, tagged
from odoo import fields

from odoo.addons.to_sales_target.tests.target_common import TargetCommon


class TestTargetSaleCommon(TargetCommon):

    @classmethod
    def setUpClass(cls):
        super(TestTargetSaleCommon, cls).setUpClass()

        partner = cls.env['res.partner'].create({'name': 'Cus'})

        cls.product_sale = cls.env['product.product'].create({
            'name': 'Boudin',
            'type': 'service',
            'list_price': 5000,
            'invoice_policy': 'order',
        })
        cls.SaleOrder = cls.env['sale.order'].with_context({'default_partner_id': partner.id})

        cls.journal_sale = cls.env['account.journal'].create({
            'name': 'Sale Journal - Test',
            'code': 'AJ-SALE',
            'type': 'sale',
            'company_id': cls.env.company.id,
        })

    @classmethod
    def create_so(self, product, qty=2, user_create=False):
        so_form = Form(self.SaleOrder.with_user(user_create or self.env.user))
        with so_form.order_line.new() as line:
            line.product_id = product
            line.product_uom_qty = qty
        so_form.date_order = fields.Datetime.now()
        so = so_form.save()
        so.action_confirm()
        return so.with_user(self.env.user)

    def create_posted_invoice_from_so(self, so):
        # Create the invoicing wizard and invoice all of them at once
        context = {
            'active_model': 'sale.order',
            'active_ids': [so.id],
            'active_id': so.id,
            'default_journal_id': self.journal_sale.id,
        }
        pre_invoiced = so.invoice_ids
        wiz = self.env['sale.advance.payment.inv'].with_context(context).create({})
        wiz.create_invoices()
        just_created_invoices = so.invoice_ids - pre_invoiced
        just_created_invoices.invoice_date = fields.Datetime.now()
        just_created_invoices.action_post()
        return just_created_invoices

    def form_create_team_target_approve(self, sale_team, start_date, end_date, target=100, user_create=False):
        team_target = self.form_create_team_target(sale_team=sale_team, start_date=start_date, end_date=end_date, target=target, user_create=user_create)
        team_target.action_confirm()
        team_target.action_approve()
        return team_target
