from datetime import date

from odoo.addons.to_loan_management.tests.common import TestLoanCommon
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged


class TestLoanBorrowingOrder(TestLoanCommon):

    @classmethod
    def setUpClass(cls, company=None):
        super().setUpClass(company=company)
        cls.env.company.write({
            'loan_borrowing_journal_id': cls.journal_loan_borrow.id,
            'loan_borrowing_account_id': cls.account_loan_borrow.id,
            'loan_lending_journal_id': cls.journal_loan_lend.id,
            'loan_lending_account_id': cls.account_loan_lend.id,
        })
        cls.loan_order_month_flat = cls.create_loan_order_form(100000000, cls.interest_fixed_rate_type_month)
        cls.loan_order_week_flat = cls.create_loan_order_form(100000000, cls.interest_fixed_rate_type_week)
        cls.loan_order_year_flat = cls.create_loan_order_form(100000000, cls.interest_fixed_rate_type_year)
        cls.loan_order_month_float = cls.create_loan_order_form(100000000, cls.interest_float_rate_type_month)
        cls.loan_order_year_float = cls.create_loan_order_form(100000000, cls.interest_float_rate_type_year)
        cls.loan_order_week_float = cls.create_loan_order_form(100000000, cls.interest_float_rate_type_week)

    @classmethod
    def create_loan_order_form(cls, loan_amount, interest_rate_type, loan_duration=None):
        loan_order_form = Form(cls.env['loan.borrowing.order'])
        loan_order_form.partner_id = cls.partner
        loan_order_form.date_confirmed = date(2021, 10, 15)
        loan_order_form.loan_amount = loan_amount
        loan_order_form.interest_rate_type_id = interest_rate_type
        loan_order_form.expiry_interest_rate_type_id = interest_rate_type
        if loan_duration:
            loan_order_form.loan_duration = loan_duration
        return loan_order_form.save()

    def create_disburement(self, loan_order, amount, custom_value=None):
        if custom_value is None:
            custom_value = {}
        value = {
            'order_id': loan_order.id,
            'amount': amount,
        }
        if custom_value:
            value.update(custom_value)
        return self.env['loan.borrow.disbursement'].with_context(tracking_disable=True).create(value)

    def create_disbursement_payment_wizard_form(self, loan_order_or_disburement, journal, amount=None, currency=None,
                                                custom_value=None):
        if custom_value is None:
            custom_value = {}
        action_disbursement_register = loan_order_or_disburement.action_disbursement_register_wizard()
        action_disbursement_register['context'].update(custom_value)
        disbursement_payment_wizard_form = Form(
            self.env[action_disbursement_register['res_model']].with_context(action_disbursement_register['context']))
        disbursement_payment_wizard_form.journal_id = journal
        disbursement_payment_wizard_form.payment_date = date(2021, 10, 15)
        if amount:
            disbursement_payment_wizard_form.amount = amount
        if currency:
            disbursement_payment_wizard_form.currency_id = currency
        disdisbursement_payment_wizard = disbursement_payment_wizard_form.save()
        disdisbursement_payment_wizard.action_payment_create_and_match()
        return disdisbursement_payment_wizard

    def create_refund_payment_wizard_form(self, refund, journal, amount=None, currency=None,
                                          custom_value=None):
        if custom_value is None:
            custom_value = {}
        refund_register_wizard = refund.action_refund_register_wizard()
        refund_register_wizard['context'].update(custom_value)
        refund_register_wizard_form = Form(
            self.env[refund_register_wizard['res_model']].with_context(refund_register_wizard['context']))
        refund_register_wizard_form.journal_id = journal
        refund_register_wizard_form.payment_date = date(2021, 10, 15)
        if amount:
            refund_register_wizard_form.amount = amount
        if currency:
            refund_register_wizard_form.currency_id = currency
        disbursement_payment_wizard = refund_register_wizard_form.save()
        disbursement_payment_wizard.action_payment_create_and_match()
        return disbursement_payment_wizard

    def create_interest_invoice(self, interest):
        interest_invoicing_wizard = interest.action_invoice()
        interest_invoicing_wizard_form = Form(
            self.env[interest_invoicing_wizard['res_model']].with_context(interest_invoicing_wizard['context']))
        interest_invoicing_wizard = interest_invoicing_wizard_form.save()
        interest_invoicing_wizard.create_invoices()
        return interest.invoice_ids

    def create_payment(self, amount, invoice):
        payment = self.env['account.payment'].with_context(tracking_disable=True).create({
            'amount': amount,
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'payment_method_id': self.account_payment_method_manual_in.id,
            'journal_id': self.journal_bank.id,
            'date': invoice.date
        })
        payment.action_post()
        (invoice | payment.move_id).line_ids.filtered(lambda r:r.account_id == payment.destination_account_id).reconcile()
        return payment

    def test_loan_order_form(self):
        loan_order = self.loan_order_month_flat
        self.assertRecordValues(loan_order,
                                [{'product_id': self.interest_fixed_rate_type_month.product_id.id,
                                  'journal_id': self.journal_loan_borrow.id,
                                  'account_id': self.account_loan_borrow.id}]
                                )
        loan_order.write({'disbursement_start_date': date(2021, 10, 20)})
        self.assertEqual(loan_order.date_end, date(2022, 10, 19))

    def test_disbursement_start_date_earlier_than_contract_start_date(self):
        loan_order = self.loan_order_month_flat
        with self.assertRaises(ValidationError):
            loan_order.write({'disbursement_start_date': date(2021, 10, 14)})

    def test_disbursement_more_than_loan_amount(self):
        loan_order = self.loan_order_month_flat
        with self.assertRaises(ValidationError):
            self.create_disburement(loan_order, 200000000)

    def test_disbursement_end_date(self):
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_method': 'end',
            'disbursement_method_number': 2,
            'disbursement_method_period': 2,
            'disbursement_end_date': date(2022, 9, 18)
        })
        loan_order.action_compute_data_line()
        self.assertEqual(loan_order.disbursement_start_date, date(2022, 7, 18))
        self.assertRecordValues(loan_order.disbursement_line_ids,
                                [{'amount': 50000000, 'date': date(2022, 7, 18)},
                                 {'amount': 50000000, 'date': date(2022, 9, 18)}, ])
        loan_order.action_compute_data_line()
        self.assertEqual(loan_order.loan_amount, 100000000)
        self.assertRecordValues(loan_order.disbursement_line_ids,
                                [{'amount': 50000000, 'date': date(2022, 7, 18)},
                                 {'amount': 50000000, 'date': date(2022, 9, 18)}, ])

    def test_disbursement_by_number(self):
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_method_number': 2,
            'disbursement_method_period': 2,
            'disbursement_start_date': date(2022, 7, 18)
        })
        loan_order.action_compute_data_line()
        self.assertEqual(loan_order.disbursement_start_date, date(2022, 7, 18))
        self.assertRecordValues(loan_order.disbursement_line_ids,
                                [{'amount': 50000000, 'date': date(2022, 7, 18)},
                                 {'amount': 50000000, 'date': date(2022, 9, 18)}, ])

    def test_compute_refund_vs_interest_but_not_set_date_for_disbursement(self):
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_method': 'upon_request',
        })
        loan_order.action_compute_data_line()
        self.assertFalse(loan_order.disbursement_line_ids)
        self.create_disburement(loan_order, 100000000)
        with self.assertRaises(UserError, msg="not set date for disbursement"):
            loan_order.action_compute_data_line()

    def test_disbursement_upon_request(self):
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_method': 'upon_request',
        })
        loan_order.action_compute_data_line()
        self.create_disburement(loan_order, 100000000, custom_value={'date_maturity': date(2021, 10, 15)})
        loan_order.action_compute_data_line()
        self.assertTrue(loan_order.disbursement_line_ids)
        self.assertTrue(loan_order.refund_line_ids)
        self.assertTrue(loan_order.interest_line_ids)

    def test_confirm_contract(self):
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_method_number': 2,
            'disbursement_method_period': 2,
            'disbursement_start_date': date(2022, 7, 18)
        })
        loan_order.action_confirm()
        self.assertEqual(loan_order.state, 'confirmed')
        self.assertEqual(len(loan_order.disbursement_line_ids), 2)
        self.assertRecordValues(loan_order.disbursement_line_ids,
                                [{'state': 'confirmed'}, {'state': 'confirmed'}])

    def test_unlink_disburement(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_compute_data_line()
        loan_order.disbursement_line_ids.unlink()
        self.assertFalse(loan_order.refund_line_ids)
        self.assertFalse(loan_order.interest_line_ids)

    def test_cannot_unlink_not_in_draft_state(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        with self.assertRaises(UserError):
            loan_order.unlink()
        with self.assertRaises(UserError):
            loan_order.disbursement_line_ids.unlink()

    def test_cannot_mark_as_done_01(self):
        loan_order = self.loan_order_month_flat
        with self.assertRaises(UserError, msg="Loan order not confirmed"):
            loan_order.action_done()
        loan_order.action_confirm()
        with self.assertRaises(UserError, msg="Existing Disbursement confirmed"):
            loan_order.action_done()
        loan_order.disbursement_line_ids.action_cancel()
        loan_order.action_done()

    def test_cannot_mark_as_done_02(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank)
        with self.assertRaises(UserError, msg="Existing Refund confirmed"):
            loan_order.action_done()

    def test_cannot_mark_as_done_03(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        self.assertGreater(len(loan_order.interest_line_ids), 1)
        self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank)
        loan_order.interest_line_ids[0].action_confirm()
        loan_order.interest_line_ids[0].action_cancel()
        loan_order.refund_line_ids.action_cancel()
        loan_order.action_done()
        self.assertEqual(len(loan_order.interest_line_ids), 1)

    def test_can_mark_as_done(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        self.assertGreater(len(loan_order.interest_line_ids), 1)
        self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank)
        loan_order.interest_line_ids[0].action_confirm()
        loan_order.refund_line_ids.action_cancel()
        with self.assertRaises(UserError, msg="Existing Interests confirmed"):
            loan_order.action_done()

    def test_cannot_confirm_interest_line(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        with self.assertRaises(ValidationError):
            loan_order.interest_line_ids[0].action_confirm()

    def test_cannot_confirm_refund_line(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        with self.assertRaises(UserError):
            loan_order.refund_line_ids[0].action_confirm()

    def test_interest_fixed_rate_01(self):
        """
        Interest Rate Type: week
        Interest Cycle: week
        """
        loan_order = self.loan_order_week_flat
        loan_order.write({
            'loan_duration': 1,
            'interest_cycle': 'weekly',
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.disbursement_line_ids,
                                [{'amount': 100000000, 'date': date(2022, 8, 19)}])
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 200000, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 8, 21),
                                  'daily_rate': 0.1}])
        self.assertTrue(all(line.amount == 700000 for line in loan_order.interest_line_ids[1:-1]))
        self.assertEqual(loan_order.interest_line_ids[-1].amount, 700000)

    def test_interest_fixed_rate_02(self):
        """
        Interest Rate Type: month
        Interest Cycle: month
        """
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 3870967.74, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 8, 31),
                                  'daily_rate': 0.3225806451612904}])
        self.assertTrue(all(line.amount == 10000000 for line in loan_order.interest_line_ids[1:-1]))
        self.assertRecordValues(loan_order.interest_line_ids[-1],
                                [{'amount': 5806451.61, 'date_from': date(2023, 8, 1), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.3225806451612904}])

    def test_interest_fixed_rate_03(self):
        """
        Interest Rate Type: year
        Interest Cycle: month
        """
        loan_order = self.loan_order_year_flat
        loan_order.write({
            'interest_cycle': 'monthly',
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 387096.77, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 8, 31),
                                  'daily_rate': 0.03225806451612904}])
        self.assertTrue(all(line.amount == 1000000 for line in loan_order.interest_line_ids[1:-1]))
        self.assertRecordValues(loan_order.interest_line_ids[-1],
                                [{'amount': 580645.16, 'date_from': date(2023, 8, 1), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.03225806451612904}])

    def test_interest_fixed_rate_04(self):
        """
        Interest Rate Type: month
        Interest Cycle: quarterly
        """
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'interest_cycle': 'quarterly',
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids, [
            {'amount': 13548387.1, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 9, 30), 'nbr_of_days': 42,
             'daily_rate': 0.3225806451612904},
            {'amount': 29677419.35, 'date_from': date(2022, 10, 1), 'date_to': date(2022, 12, 31), 'nbr_of_days': 92,
             'daily_rate': 0.3225806451612904},
            {'amount': 29032258.06, 'date_from': date(2023, 1, 1), 'date_to': date(2023, 3, 31), 'nbr_of_days': 90,
             'daily_rate': 0.3225806451612904},
            {'amount': 30333333.33, 'date_from': date(2023, 4, 1), 'date_to': date(2023, 6, 30), 'nbr_of_days': 91,
             'daily_rate': 0.33333333333333337},
            {'amount': 15806451.61, 'date_from': date(2023, 7, 1), 'date_to': date(2023, 8, 18), 'nbr_of_days': 49,
             'daily_rate': 0.3225806451612904},
        ])

    def test_interest_fixed_rate_05(self):
        """
        Interest Rate Type: year
        Interest Cycle: year
        """
        loan_order = self.loan_order_year_flat
        loan_order.write({
            'interest_cycle': 'annually',
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids,
                                [{'amount': 4405479.45, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 12, 31),
                                  'daily_rate': 0.03287671232876712},
                                 {'amount': 7561643.84, 'date_from': date(2023, 1, 1), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.03287671232876712}])

    def test_interest_fixed_rate_08(self):
        """
        Interest Rate Type: month
        Interest Cycle: month
        Fixed Days of Month: 28
        """
        self.interest_float_rate_type_week.write({
            'fixed_days_of_month': True,
            'days_of_month': 28
        })
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 3870967.74, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 8, 31),
                                  'daily_rate': 0.3225806451612904}])
        self.assertTrue(all(line.amount == 10000000 for line in loan_order.interest_line_ids[1:-1]))
        self.assertRecordValues(loan_order.interest_line_ids[-1],
                                [{'amount': 5806451.61, 'date_from': date(2023, 8, 1), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.3225806451612904}])

    def test_interest_fixed_rate_09(self):
        """
        Interest Rate Type: year
        Interest Cycle: year
        Fixed Days of Month: 28
        """
        self.interest_float_rate_type_week.write({
            'fixed_days_of_month': True,
            'days_of_month': 28
        })
        loan_order = self.loan_order_year_flat
        loan_order.write({
            'interest_cycle': 'annually',
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids,
                                [{'amount': 4405479.45, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 12, 31),
                                  'daily_rate': 0.03287671232876712},
                                 {'amount': 7561643.84, 'date_from': date(2023, 1, 1), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.03287671232876712}])

    def test_interest_fixed_rate_10(self):
        """
        Interest Rate Type: week
        Interest Cycle: week
        Fixed Days of Year: 360
        """
        self.interest_float_rate_type_week.write({
            'fixed_days_of_year': True,
            'days_of_year': 360
        })
        loan_order = self.loan_order_week_flat
        loan_order.write({
            'loan_duration': 1,
            'interest_cycle': 'weekly',
            'disbursement_method': 'number',
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 200000, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 8, 21),
                                  'daily_rate': 0.1}])
        self.assertTrue(all(line.amount == 700000 for line in loan_order.interest_line_ids[1:]))

    def test_interest_fixed_rate_11(self):
        """
        Interest Rate Type: month
        Interest Cycle: month
        Fixed Days of Year: 360
        """
        self.interest_float_rate_type_week.write({
            'fixed_days_of_year': True,
            'days_of_year': 360
        })
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 3870967.74, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 8, 31),
                                  'daily_rate': 0.3225806451612904}])
        self.assertTrue(all(line.amount == 10000000 for line in loan_order.interest_line_ids[1:-1]))
        self.assertRecordValues(loan_order.interest_line_ids[-1],
                                [{'amount': 5806451.61, 'date_from': date(2023, 8, 1), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.3225806451612904}])

    def test_interest_fixed_rate_12(self):
        """
        Interest Rate Type: year
        Interest Cycle: year
        Fixed Days of Year: 360
        """
        self.interest_float_rate_type_week.write({
            'fixed_days_of_year': True,
            'days_of_year': 360
        })
        loan_order = self.loan_order_year_flat
        loan_order.write({
            'interest_cycle': 'annually',
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids,
                                [{'amount': 4405479.45, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 12, 31),
                                  'daily_rate': 0.03287671232876712},
                                 {'amount': 7561643.84, 'date_from': date(2023, 1, 1), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.03287671232876712}])

    def test_interest_fixed_rate_13(self):
        """
        Interest Rate Type: year
        Interest Cycle: year
        Fixed Days of Year: 360
        Fixed Days of Month: 28
        """
        self.interest_float_rate_type_week.write({
            'fixed_days_of_year': True,
            'days_of_year': 360,
            'fixed_days_of_month': True,
            'days_of_month': 28
        })
        loan_order = self.loan_order_year_flat
        loan_order.write({
            'interest_cycle': 'annually',
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids,
                                [{'amount': 4405479.45, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 12, 31),
                                  'daily_rate': 0.03287671232876712},
                                 {'amount': 7561643.84, 'date_from': date(2023, 1, 1), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.03287671232876712}])

    def test_interest_fixed_rate_14(self):
        """
        Interest Rate Type: year
        Interest Cycle: year
        Fixed Days of Year: 365
        Fixed Days of Month: 28
        """
        self.interest_float_rate_type_week.write({
            'fixed_days_of_year': True,
            'days_of_year': 365,
            'fixed_days_of_month': True,
            'days_of_month': 28
        })
        loan_order = self.loan_order_year_flat
        loan_order.write({
            'interest_cycle': 'annually',
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids,
                                [{'amount': 4405479.45, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 12, 31),
                                  'daily_rate': 0.03287671232876712},
                                 {'amount': 7561643.84, 'date_from': date(2023, 1, 1), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.03287671232876712}])

    def test_interest_fixed_rate_16(self):
        """
        Interest Rate Type: month
        Interest Cycle: month
        Fixed Days of Year: 360
        Fixed Days of Month: 28
        """
        self.interest_float_rate_type_week.write({
            'fixed_days_of_year': True,
            'days_of_year': 360,
            'fixed_days_of_month': True,
            'days_of_month': 28
        })
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_start_date': date(2022, 8, 19),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 3870967.74, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 8, 31),
                                  'daily_rate': 0.3225806451612904}])
        self.assertTrue(all(line.amount == 10000000 for line in loan_order.interest_line_ids[1:-1]))
        self.assertRecordValues(loan_order.interest_line_ids[-1],
                                [{'amount': 5806451.61, 'date_from': date(2023, 8, 1), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.3225806451612904}])

    def test_interest_fixed_rate_18(self):
        """
        Interest Rate Type: year
        Interest Cycle: month
        """
        loan_order = self.loan_order_year_flat
        loan_order.write({
            'interest_cycle': 'monthly',
            'disbursement_start_date': date(2022, 8, 19),
            'principal_refund_method': 'number',
            'principal_refund_method_number': 2,
            'principal_refund_method_period': 6
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 387096.77, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 8, 31),
                                  'daily_rate': 0.03225806451612904}])
        self.assertTrue(all(line.amount == 1000000 for line in loan_order.interest_line_ids[1:6]))
        self.assertRecordValues(loan_order.interest_line_ids[6],
                                [{'amount': 642857.14, 'date_from': date(2023, 2, 1), 'date_to': date(2023, 2, 18),
                                  'daily_rate': 0.035714285714285726}])
        self.assertRecordValues(loan_order.interest_line_ids[7],
                                [{'amount': 178571.43, 'date_from': date(2023, 2, 19), 'date_to': date(2023, 2, 28),
                                  'daily_rate': 0.035714285714285726}])
        self.assertTrue(all(line.amount == 500000 for line in loan_order.interest_line_ids[8:-1]))
        self.assertRecordValues(loan_order.interest_line_ids[-1],
                                [{'amount': 290322.58, 'date_from': date(2023, 8, 1), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.03225806451612904}])

    def test_interest_fixed_rate_19(self):
        """
        Interest Rate Type: year
        Interest Cycle: year
        Refund Numbers: 2
        """
        loan_order = self.loan_order_year_flat
        loan_order.write({
            'interest_cycle': 'annually',
            'disbursement_start_date': date(2022, 8, 19),
            'principal_refund_method': 'number',
            'principal_refund_method_number': 2,
            'principal_refund_method_period': 6
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids,
                                [{'amount': 4405479.45, 'date_from': date(2022, 8, 20), 'date_to': date(2022, 12, 31),
                                  'daily_rate': 0.03287671232876712},
                                 {'amount': 1610958.9000000001, 'date_from': date(2023, 1, 1),
                                  'date_to': date(2023, 2, 18),
                                  'daily_rate': 0.03287671232876712},
                                 {'amount': 2975342.47, 'date_from': date(2023, 2, 19), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.03287671232876712}])

    def test_interest_fixed_rate_20(self):
        """
        Interest Rate Type: year
        Interest Cycle: year
        Refund Numbers: 2
        Include Disbursement Date: True
        """
        loan_order = self.loan_order_year_flat
        loan_order.write({
            'interest_cycle': 'annually',
            'disbursement_start_date': date(2022, 8, 19),
            'principal_refund_method': 'number',
            'principal_refund_method_number': 2,
            'principal_refund_method_period': 6,
            'interest_incl_disburment_date': True
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids,
                                [{'amount': 4438356.16, 'date_from': date(2022, 8, 19), 'date_to': date(2022, 12, 31),
                                  'daily_rate': 0.03287671232876712},
                                 {'amount': 1610958.9000000001, 'date_from': date(2023, 1, 1),
                                  'date_to': date(2023, 2, 18),
                                  'daily_rate': 0.03287671232876712},
                                 {'amount': 2975342.47, 'date_from': date(2023, 2, 19), 'date_to': date(2023, 8, 18),
                                  'daily_rate': 0.03287671232876712}])

    def test_interest_fixed_rate_21(self):
        """
        Disbursement Start date: last date of month
        Interest Rate Type: month
        Interest Cycle: month
        """
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_start_date': date(2021, 10, 30),
            'loan_duration': 3,
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids, [
            {'amount': 322580.65, 'date_from': date(2021, 10, 31), 'date_to': date(2021, 10, 31),
             'daily_rate': 0.3225806451612904},
            {'amount': 10000000.0, 'date_from': date(2021, 11, 1), 'date_to': date(2021, 11, 30),
             'daily_rate': 0.33333333333333337},
            {'amount': 10000000.0, 'date_from': date(2021, 12, 1), 'date_to': date(2021, 12, 31),
             'daily_rate': 0.3225806451612904},
            {'amount': 9354838.71, 'date_from': date(2022, 1, 1), 'date_to': date(2022, 1, 29),
             'daily_rate': 0.3225806451612904},
        ])

    def test_interest_floating_rate_01(self):
        """
        Interest Rate Type: week
        Interest Cycle: weekly
        """
        loan_order = self.loan_order_week_float
        loan_order.write({
            'loan_duration': 2,
            'interest_cycle': 'weekly',
            'disbursement_start_date': date(2022, 10, 14),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 200000, 'daily_rate': 0.1}])
        self.assertRecordValues(loan_order.interest_line_ids[7],
                                [{'amount': 200000, 'date_from': date(2022, 11, 28), 'date_to': date(2022, 11, 29),
                                  'daily_rate': 0.1}])
        self.assertRecordValues(loan_order.interest_line_ids[8],
                                [{'amount': 1000000, 'date_from': date(2022, 11, 30), 'date_to': date(2022, 12, 4),
                                  'daily_rate': 0.2}])
        self.assertRecordValues(loan_order.interest_line_ids[-1],
                                [{'amount': 400000.0, 'date_from': date(2022, 12, 12), 'date_to': date(2022, 12, 13),
                                  'daily_rate': 0.2}])

    def test_interest_floating_rate_02(self):
        """
        Interest Rate Type: month
        Interest Cycle: monthly
        """
        loan_order = self.loan_order_month_float
        loan_order.write({
            'disbursement_start_date': date(2021, 10, 16),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 2419354.84, 'daily_rate': 0.1612903225806452}])
        self.assertRecordValues(loan_order.interest_line_ids[1],
                                [{'amount': 5000000.0, 'daily_rate': 0.16666666666666669}])
        self.assertRecordValues(loan_order.interest_line_ids[6],
                                [{'amount': 2333333.33, 'date_from': date(2022, 4, 1), 'date_to': date(2022, 4, 14),
                                  'daily_rate': 0.16666666666666669}])
        self.assertRecordValues(loan_order.interest_line_ids[7],
                                [{'amount': 5333333.33, 'date_from': date(2022, 4, 15), 'date_to': date(2022, 4, 30),
                                  'daily_rate': 0.33333333333333337}])
        self.assertRecordValues(loan_order.interest_line_ids[8],
                                [{'amount': 10000000.0, 'daily_rate': 0.3225806451612904}])
        self.assertRecordValues(loan_order.interest_line_ids[-1],
                                [{'amount': 645161.29, 'date_from': date(2022, 10, 15), 'date_to': date(2022, 10, 15),
                                  'daily_rate': 0.6451612903225808}])

    def test_interest_floating_rate_03(self):
        """
        Interest Rate Type: year
        Interest Cycle: annually
        """
        loan_order = self.loan_order_year_float
        loan_order.write({
            'interest_cycle': 'annually',
            'disbursement_start_date': date(2021, 10, 16),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids,
                                [{'amount': 4164383.56, 'date_from': date(2021, 10, 17), 'date_to': date(2021, 12, 31),
                                  'daily_rate': 0.054794520547945216},
                                 {'amount': 5698630.14, 'date_from': date(2022, 1, 1), 'date_to': date(2022, 4, 14),
                                  'daily_rate': 0.054794520547945216},
                                 {'amount': 20054794.52, 'date_from': date(2022, 4, 15), 'date_to': date(2022, 10, 14),
                                  'daily_rate': 0.10958904109589043},
                                 {'amount': 164383.56, 'date_from': date(2022, 10, 15), 'date_to': date(2022, 10, 15),
                                  'daily_rate': 0.16438356164383566}])

    def test_interest_floating_rate_04(self):
        """
        Interest Rate Type: week
        Interest Cycle: weekly
        Fixed Days of Year: 360
        Fixed Days of Month: 28
        """
        self.interest_float_rate_type_week.write({
            'fixed_days_of_year': True,
            'days_of_year': 360,
            'fixed_days_of_month': True,
            'days_of_month': 28
        })
        loan_order = self.loan_order_week_float
        loan_order.write({
            'loan_duration': 2,
            'interest_cycle': 'weekly',
            'disbursement_start_date': date(2022, 10, 14),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 200000, 'daily_rate': 0.1}])
        self.assertRecordValues(loan_order.interest_line_ids[7],
                                [{'amount': 200000, 'date_from': date(2022, 11, 28), 'date_to': date(2022, 11, 29),
                                  'daily_rate': 0.1}])
        self.assertRecordValues(loan_order.interest_line_ids[8],
                                [{'amount': 1000000, 'date_from': date(2022, 11, 30), 'date_to': date(2022, 12, 4),
                                  'daily_rate': 0.2}])
        self.assertRecordValues(loan_order.interest_line_ids[-1],
                                [{'amount': 400000, 'date_from': date(2022, 12, 12), 'date_to': date(2022, 12, 13),
                                  'daily_rate': 0.2}])

    def test_interest_floating_rate_05(self):
        """
        Interest Rate Type: month
        Interest Cycle: monthly
        Fixed Days of Year: 360
        Fixed Days of Month: 28
        """
        self.interest_float_rate_type_month.write({
            'fixed_days_of_year': True,
            'days_of_year': 360,
            'fixed_days_of_month': True,
            'days_of_month': 28
        })
        loan_order = self.loan_order_month_float
        loan_order.write({
            'disbursement_start_date': date(2021, 10, 16),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids[0],
                                [{'amount': 2678571.43, 'date_from': date(2021, 10, 17), 'date_to': date(2021, 10, 31),
                                  'daily_rate': 0.1785714285714286}])
        self.assertRecordValues(loan_order.interest_line_ids[1],
                                [{'amount': 5000000.0, 'date_from': date(2021, 11, 1), 'date_to': date(2021, 11, 30),
                                  'daily_rate': 0.1785714285714286}])
        self.assertRecordValues(loan_order.interest_line_ids[6],
                                [{'amount': 2500000.0, 'date_from': date(2022, 4, 1), 'date_to': date(2022, 4, 14),
                                  'daily_rate': 0.1785714285714286}])
        self.assertRecordValues(loan_order.interest_line_ids[7],
                                [{'amount': 5714285.71, 'date_from': date(2022, 4, 15), 'date_to': date(2022, 4, 30),
                                  'daily_rate': 0.3571428571428572}])
        self.assertRecordValues(loan_order.interest_line_ids[8],
                                [{'amount': 10000000.0, 'daily_rate': 0.3571428571428572}])
        self.assertRecordValues(loan_order.interest_line_ids[-1],
                                [{'amount': 714285.71, 'date_from': date(2022, 10, 15), 'date_to': date(2022, 10, 15),
                                  'daily_rate': 0.7142857142857144}])

    def test_interest_floating_rate_06(self):
        """
        Interest Rate Type: year
        Interest Cycle: annually
        Fixed Days of Year: 360
        Fixed Days of Month: 28
        """
        self.interest_float_rate_type_year.write({
            'fixed_days_of_year': True,
            'days_of_year': 360,
            'fixed_days_of_month': True,
            'days_of_month': 28
        })
        loan_order = self.loan_order_year_float
        loan_order.write({
            'interest_cycle': 'annually',
            'disbursement_start_date': date(2021, 10, 16),
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids,
                                [{'amount': 4222222.22, 'date_from': date(2021, 10, 17), 'date_to': date(2021, 12, 31),
                                  'daily_rate': 0.05555555555555556},
                                 {'amount': 5777777.78, 'date_from': date(2022, 1, 1), 'date_to': date(2022, 4, 14),
                                  'daily_rate': 0.05555555555555556},
                                 {'amount': 20333333.330000002, 'date_from': date(2022, 4, 15),
                                  'date_to': date(2022, 10, 14),
                                  'daily_rate': 0.11111111111111112},
                                 {'amount': 166666.67, 'date_from': date(2022, 10, 15), 'date_to': date(2022, 10, 15),
                                  'daily_rate': 0.16666666666666669}])

    def test_interest_floating_rate_07(self):
        """
        Interest Rate Type: year
        Interest Cycle: annually
        Fixed Days of Year: 360
        Fixed Days of Month: 28
        Include Disbursement Date: True
        Refund Numbers: 2
        """
        self.interest_float_rate_type_week.write({
            'fixed_days_of_year': True,
            'days_of_year': 360,
            'fixed_days_of_month': True,
            'days_of_month': 28
        })
        loan_order = self.loan_order_year_float
        loan_order.write({
            'interest_cycle': 'annually',
            'disbursement_start_date': date(2021, 10, 16),
            'interest_incl_disburment_date': True,
            'principal_refund_method': 'number',
            'principal_refund_method_number': 2,
            'principal_refund_method_period': 6,
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids,
                                [{'amount': 4219178.08, 'date_from': date(2021, 10, 16), 'date_to': date(2021, 12, 31),
                                  'daily_rate': 0.054794520547945216},
                                 {'amount': 5698630.14, 'date_from': date(2022, 1, 1), 'date_to': date(2022, 4, 14),
                                  'daily_rate': 0.054794520547945216},
                                 {'amount': 109589.04000000001, 'date_from': date(2022, 4, 15),
                                  'date_to': date(2022, 4, 15),
                                  'daily_rate': 0.10958904109589043},
                                 {'amount': 9972602.74, 'date_from': date(2022, 4, 16), 'date_to': date(2022, 10, 14),
                                  'daily_rate': 0.10958904109589043},
                                 {'amount': 82191.78, 'date_from': date(2022, 10, 15),
                                  'date_to': date(2022, 10, 15),
                                  'daily_rate': 0.16438356164383566}])

    def test_cannot_disbursement_register_currency_diff(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        with self.assertRaises(ValidationError):
            self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank, currency=self.currency_vnd)

    def test_disbursement_register(self):
        """
        Register Disbursement for 1 disbursement line 2 times
        """
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank, amount=50000000)
        self.assertEqual(loan_order.disbursement_line_ids.state, 'confirmed')
        self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank)
        self.assertEqual(loan_order.disbursement_line_ids.state, 'paid')
        self.assertRecordValues(loan_order.disbursement_payment_match_ids, [
            {'matched_amount': 50000000, 'payment_date': date(2021, 10, 15)},
            {'matched_amount': 50000000, 'payment_date': date(2021, 10, 15)}
        ])
        self.assertRecordValues(loan_order.disbursement_line_ids.move_ids[0], [
            {'journal_id': self.journal_bank.id, 'date': date(2021, 10, 15)},
        ])
        self.assertRecordValues(loan_order.disbursement_line_ids.move_ids[0].line_ids, [
            {'date': date(2021, 10, 15), 'credit': 50000000,
             'debit': 0, 'account_id': self.account_loan_borrow.id},
            {'date': date(2021, 10, 15), 'credit': 0,
             'debit': 50000000, 'account_id': self.journal_bank.payment_debit_account_id.id},
        ])

    def test_disbursement_register_2(self):
        """
        Register Disbursement for 2 Disbursement lines
        """
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_method_number': 2,
            'disbursement_method_period': 2,
        })
        loan_order.action_confirm()
        self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank)
        self.assertRecordValues(loan_order.disbursement_line_ids, [
            {'state': 'paid'},
            {'state': 'paid'},
        ])
        self.assertRecordValues(loan_order.disbursement_payment_match_ids, [
            {'matched_amount': 50000000, 'payment_date': date(2021, 10, 15)},
            {'matched_amount': 50000000, 'payment_date': date(2021, 10, 15)}
        ])
        self.assertRecordValues(loan_order.disbursement_line_ids.move_ids, [
            {'journal_id': self.journal_bank.id, 'date': date(2021, 10, 15)},
        ])
        self.assertRecordValues(loan_order.disbursement_line_ids.move_ids.line_ids, [
            {'date': date(2021, 10, 15), 'credit': 50000000,
             'debit': 0, 'account_id': self.account_loan_borrow.id},
            {'date': date(2021, 10, 15), 'credit': 50000000,
             'debit': 0, 'account_id': self.account_loan_borrow.id},
            {'date': date(2021, 10, 15), 'credit': 0,
             'debit': 100000000, 'account_id': self.journal_bank.payment_debit_account_id.id},
        ])

    def test_disbursement_register_3(self):
        """
        Register Disbursement from disbursement form
        """
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'disbursement_method_number': 2,
            'disbursement_method_period': 2,
        })
        loan_order.action_confirm()
        self.create_disbursement_payment_wizard_form(loan_order.disbursement_line_ids[0], self.journal_bank)
        self.assertEqual(loan_order.disbursement_line_ids[0].state, 'paid')
        self.assertRecordValues(loan_order.disbursement_payment_match_ids, [
            {'matched_amount': 50000000, 'payment_date': date(2021, 10, 15)},
        ])
        self.assertRecordValues(loan_order.disbursement_line_ids.move_ids, [
            {'journal_id': self.journal_bank.id, 'date': date(2021, 10, 15)},
        ])
        self.assertRecordValues(loan_order.disbursement_line_ids.move_ids.line_ids, [
            {'date': date(2021, 10, 15), 'credit': 50000000,
             'debit': 0, 'account_id': self.account_loan_borrow.id},
            {'date': date(2021, 10, 15), 'credit': 0,
             'debit': 50000000, 'account_id': self.journal_bank.payment_debit_account_id.id},
        ])

    def test_cancel_disbursement_payment_match(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank)
        loan_order.disbursement_payment_match_ids.payment_id.action_cancel()
        loan_order.disbursement_line_ids.action_cancel()
        loan_order.disbursement_line_ids.action_draft()
        loan_order.disbursement_line_ids.action_confirm()
        loan_order.disbursement_line_ids.with_context(regenerate=True).action_generate_refund_lines()

    def test_refund_payment(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        with self.assertRaises(UserError):
            loan_order.refund_line_ids.action_confirm()
        self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank)
        self.create_refund_payment_wizard_form(loan_order.refund_line_ids, self.journal_bank)
        self.assertEqual(loan_order.disbursement_line_ids.state, 'refunded')
        self.assertRecordValues(loan_order.refund_payment_match_ids, [
            {'matched_amount': 100000000, 'payment_date': date(2021, 10, 15)},
        ])

    def test_interest_payment(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        with self.assertRaises(ValidationError):
            loan_order.interest_line_ids.action_confirm()
        self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank)
        with self.assertRaises(ValidationError):
            self.create_interest_invoice(loan_order.interest_line_ids[0])
        loan_order.interest_line_ids.action_confirm()
        self.assertEqual(loan_order.interest_line_ids[0].state, 'confirmed')
        invoice = self.create_interest_invoice(loan_order.interest_line_ids[0])
        self.assertEqual(loan_order.interest_line_ids[0].state, 'confirmed')
        invoice.invoice_date = invoice.date
        invoice.action_post()
        self.create_payment(100000000, invoice)
        self.assertEqual(loan_order.interest_line_ids[0].state, 'paid')

    def test_cancel_invoice_of_interest_line(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank)
        loan_order.interest_line_ids.action_confirm()
        invoice = self.create_interest_invoice(loan_order.interest_line_ids[0])
        invoice.invoice_date = invoice.date
        invoice.action_post()
        self.create_payment(100000000, invoice)
        self.assertEqual(loan_order.interest_line_ids[0].state, 'paid')
        invoice.button_draft()
        self.assertEqual(loan_order.interest_line_ids[0].state, 'confirmed')

    def test_cancel_interest(self):
        """
        Hủy dòng lãi suất -> hủy bút toán liên quan
        """
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        self.create_disbursement_payment_wizard_form(loan_order, self.journal_bank)
        loan_order.interest_line_ids.action_confirm()
        invoice = self.create_interest_invoice(loan_order.interest_line_ids[0])
        loan_order.interest_line_ids[0].action_cancel()
        self.assertEqual(loan_order.interest_line_ids[0].state, 'cancelled')
        self.assertEqual(invoice.state, 'cancel')

    def test_reconfirm_contract(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        loan_order.action_cancel()
        self.assertEqual(loan_order.state, 'cancelled')
        loan_order.action_draft()
        self.assertEqual(loan_order.state, 'draft')

    def test_set_days_of_month_or_year_to_zero(self):
        with self.assertRaises(UserError):
            self.interest_fixed_rate_type_month.write({
                'fixed_days_of_year': True,
                'days_of_year': 0,
                'fixed_days_of_month': True,
                'days_of_month': 0
            })

    def test_copy_contract_order(self):
        loan_order = self.loan_order_month_flat
        loan_order_copy = loan_order.copy()
        self.assertRecordValues(loan_order_copy, [
            {
                'loan_amount': 100000000,
                'currency_id': loan_order.currency_id.id,
                'journal_id': loan_order.journal_id.id,
                'account_id': loan_order.account_id.id,
                'interest_rate_type_id': loan_order.interest_rate_type_id.id,
                'disbursement_method': 'number'
            },
        ])

    def test_unlink_contract_order(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_compute_data_line()
        loan_order.unlink()

    def test_cannot_set_disbursement_to_draft(self):
        loan_order = self.loan_order_month_flat
        loan_order.action_confirm()
        loan_order.action_cancel()
        with self.assertRaises(UserError):
            loan_order.disbursement_line_ids[0].action_draft()

    def test_compute_disbursement_with_period_start_day_not_first_date(self):
        loan_order = self.loan_order_month_flat
        loan_order.write({
            'interest_period_start_day': 2,
            'loan_duration': 3
        })
        loan_order.action_compute_data_line()
        self.assertRecordValues(loan_order.interest_line_ids, [
            {'amount': 5483870.97, 'date_from': date(2021, 10, 16), 'date_to': date(2021, 11, 1),
             'daily_rate': 0.3225806451612904},
            {'amount': 10000000.0, 'date_from': date(2021, 11, 2), 'date_to': date(2021, 12, 1),
             'daily_rate': 0.33333333333333337},
            {'amount': 10000000.0, 'date_from': date(2021, 12, 2), 'date_to': date(2022, 1, 1),
             'daily_rate': 0.3225806451612904},
            {'amount': 4193548.39, 'date_from': date(2022, 1, 2), 'date_to': date(2022, 1, 14),
             'daily_rate': 0.3225806451612904},
        ])
