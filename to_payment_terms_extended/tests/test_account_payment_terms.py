from odoo import fields
from odoo.tests.common import TransactionCase, Form, tagged


@tagged('post_install', '-at_install')
class PaymentTerm(TransactionCase):

    @staticmethod
    def _init_payment_term(self, type, value, fixed_day, month, **kwargs):
        term_form = Form(self.env['account.payment.term'])
        term_form.name = 'Payment Term'
        # remove balance line
        term_form.line_ids.remove(0)
        # add last day of next X months line
        with term_form.line_ids.new() as line:
            line.value = type
            line.value_amount = value
            line.option = 'last_day_next_x_months'
            line.number_of_next_month = month
        # add fixed day of next X months line
        with term_form.line_ids.new() as line:
            line.value = 'balance'
            line.option = 'fix_day_next_x_months'
            line.number_of_next_month = month
            line.fixed_day_of_month = fixed_day
        return term_form.save()

    def test_01_check_onchange_option(self):
        """
        This test ensures the given '_onchange_option' method will set number of days and
        day of month is 0.
        """
        term_form = self._init_payment_term(self, 'percent', 50, 35, 2)
        with Form(term_form) as term:
            with term.line_ids.edit(1) as line:
                line.option = 'last_day_next_x_months'
                self.assertEqual(line.days, 0, "Number of days not fixed to 0")
                self.assertEqual(line.fixed_day_of_month, 0, "Day of month not fixed to 0")

    def test_11_validate_compute_term(self):
        """
        This test ensures the given date and value are computed by two option (last day of next X months,
        fixed day of next X months) exactly.
        """
        term = self._init_payment_term(self, 'percent', 50, 35, 2)
        date_ref = fields.Date.from_string('2021-08-06')
        result = term.compute(value=10000.0, date_ref=date_ref)
        percent_value = 10000.0 * 50.0 / 100.0
        # option last day of next X months
        element_data_1 = result[0]
        self.assertEqual(element_data_1[0], '2021-10-31', "Date is computed from `last day of next X months` option is wrong")
        self.assertEqual(element_data_1[1], percent_value, "Value is computed from `last day of next X months` option is wrong")
        # option fixed day of next X months
        element_data_2 = result[1]
        self.assertEqual(element_data_2[0], '2021-10-31', "Date is computed from `fixed day of next X months` option is wrong")
        self.assertEqual(element_data_2[1], 10000.0 - percent_value, "Value is computed from `fixed day of next X months` option is wrong")
    
    def test_12_validate_compute_term(self):
        """
        This test ensures the given date and value are computed by two option (last day of next X months,
        fixed day of next X months) exactly.
        """
        term = self._init_payment_term(self, 'percent', 50, 20, 2)
        date_ref = fields.Date.from_string('2021-08-10')
        result = term.compute(value=10000.0, date_ref=date_ref)
        percent_value = 10000.0 * 50.0 / 100.0
        # option last day of next X months
        element_data_1 = result[0]
        self.assertEqual(element_data_1[0], '2021-10-31', "Date is computed from `last day of next X months` option is wrong")
        self.assertEqual(element_data_1[1], percent_value, "Value is computed from `last day of next X months` option is wrong")
        # option fixed day of next X months
        element_data_2 = result[1]
        self.assertEqual(element_data_2[0], '2021-10-20', "Date is computed from `fixed day of next X months` option is wrong")
        self.assertEqual(element_data_2[1], 10000.0 - percent_value, "Value is computed from `fixed day of next X months` option is wrong")
    
    def test_13_validate_compute_term(self):
        """
        This test ensures the given date and value are computed by two option (last day of next X months,
        fixed day of next X months) exactly.
        """
        term = self._init_payment_term(self, 'fixed', 3000, 20, 2)
        date_ref = fields.Date.from_string('2021-08-15')
        result = term.compute(value=10000.0, date_ref=date_ref)
        fixed_value = 3000.0
        # option last day of next X months
        element_data_1 = result[0]
        self.assertEqual(element_data_1[0], '2021-10-31', "Date is computed from `last day of next X months` option is wrong")
        self.assertEqual(element_data_1[1], fixed_value, "Value is computed from `last day of next X months` option is wrong")
        # option fixed day of next X months
        element_data_2 = result[1]
        self.assertEqual(element_data_2[0], '2021-10-20', "Date is computed from `fixed day of next X months` option is wrong")
        self.assertEqual(element_data_2[1], 10000.0 - fixed_value, "Value is computed from `fixed day of next X months` option is wrong")
