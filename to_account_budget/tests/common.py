from odoo import fields
from odoo.tests.common import Form

from odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestAccountBudgetCommon(AccountingTestCase):

    def setUp(self):
        super(TestAccountBudgetCommon, self).setUp()
        # In order to check account budget module in Odoo I created a budget with few budget positions
        # Checking if the budgetary positions have accounts or not
        self.account_revenue = self.env['account.account'].search([
            ('user_type_id', '=', self.ref('account.data_account_type_revenue')),
            ('tag_ids.name', 'in', ['Operating Activities'])
        ], limit=1)
        if not self.account_revenue:
            self.account_revenue = self.env['account.account'].create({
                'name': 'Product Sales - (test)',
                'code': 'X2020',
                'user_type_id': self.ref('account.data_account_type_revenue'),
                'tag_ids': [(6, 0, [self.ref('account.account_tag_operating')])],
            })
        self.account_revenue2 = self.env['account.account'].create({
                'name': 'Product Sales 2 - (test)',
                'code': 'X20202',
                'user_type_id': self.ref('account.data_account_type_revenue'),
                'tag_ids': [(6, 0, [self.ref('account.account_tag_operating')])],
            })
        self.account_budget_post_sales0 = self.env['account.budget.post'].create({
            'name': 'Sales',
            'account_ids': [(6, None, self.account_revenue2.ids)],
        })

        self.account_expense = self.env['account.account'].search([
            ('user_type_id.name', '=', 'Expenses'),
            ('tag_ids.name', 'in', ['Operating Activities'])
        ])

        if not self.account_expense:
            self.account_expense = self.env['account.account'].create({
                'name': 'Expense - (test)',
                'code': 'X2120',
                'user_type_id': self.ref('account.data_account_type_expenses'),
                'tag_ids': [(6, 0, [self.ref('account.account_tag_operating')])],
            })

        self.account_budget_post_purchase0 = self.env['account.budget.post'].create({
            'name': 'Purchases',
            'account_ids': [(6, None, self.account_expense.ids)],
        })

        self.pay_terms_a = self.env.ref('account.account_payment_term_immediate')

        self.partner_a = self.env['res.partner'].create({
            'name': 'partner_a',
            'property_payment_term_id': self.pay_terms_a.id,
            'property_supplier_payment_term_id': self.pay_terms_a.id,
            'company_id': False,
        })

        self.product_a = self.env['product.product'].create({
            'name': 'product_a',
            'uom_id': self.env.ref('uom.product_uom_unit').id,
            'lst_price': 1000.0,
            'standard_price': 800.0,
        })

    def _create_crossovered_budget(self, date_from, date_to, posted_items_only=False):
        return self.env['crossovered.budget'].create({
            'name': 'test budget name from %s to %s' % (date_from, date_to),
            'date_from': date_from,
            'date_to': date_to,
            'posted_items_only': posted_items_only,
        })

    def _create_crossovered_budget_line(self,
                                        budget,
                                        date_from,
                                        date_to,
                                        planned_amount,
                                        paid_date=False,
                                        analytic_account=False,
                                        general_budget=False):
        return self.env['crossovered.budget.line'].create(
            self._prepare_crossovered_budget_line_vals(budget,
                                                       date_from,
                                                       date_to,
                                                       planned_amount,
                                                       paid_date=paid_date,
                                                       analytic_account=analytic_account,
                                                       general_budget=general_budget)
            )

    def _prepare_crossovered_budget_line_vals(self,
                                              budget,
                                              date_from,
                                              date_to,
                                              planned_amount,
                                              paid_date=False,
                                              analytic_account=False,
                                              general_budget=False):
        vals = {
            'date_from': date_from,
            'date_to': date_to,
            'planned_amount': planned_amount,
            'crossovered_budget_id': budget.id,
        }
        if paid_date:
            vals['paid_date'] = paid_date
        if analytic_account:
            vals['analytic_account_id'] = analytic_account.id
        if general_budget:
            vals['general_budget_id'] = general_budget.id
        return vals

    def _create_account_analytic_line(self, account, amount, date):
        return self.env['account.analytic.line'].create({
            'name': '%s - %s' % (account.name, amount),
            'account_id': account.id,
            'amount': amount,
            'date': date,
            })

    def _init_invoice(self, move_type,
                      price_unit=1000000,
                      partner=False,
                      invoice_date=False,
                      analytic_account=False,
                      account=False):
        move_form = Form(self.env['account.move'].with_context(default_type=move_type))
        move_form.invoice_date = invoice_date or fields.Date.today()
        move_form.partner_id = partner or self.partner_a
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_a
            line_form.price_unit = price_unit
            if analytic_account:
                line_form.analytic_account_id = analytic_account
            line_form.account_id = account or self.account_revenue2
            # Removes all existing taxes in the invoice line to no change amount total
            line_form.tax_ids.clear()
        return move_form.save()
