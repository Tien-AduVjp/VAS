from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, tagged

from .payment_common import PaymentCommon


@tagged('post_install', '-at_install')
class TestPaymentFlow(PaymentCommon):

    def test_01_reconcile_payment_with_invoice_same_currency(self):
        """
        Input:
            - Payment:
                - link to SO1
                - amount = 5.000.000
            - Invoice:
                - total = 6.000.000
        Action 1:
            - reconcile 3.000.000 for invoice
        Output 1:
            - amount residual on invoice = 3.000.000
        Action 2:
            - reconcile 3.000.000 for invoice
        Output 2:
            - error
        Action 3:
            - reconcile -3.000.000 for invoice
        Output 3:
            - error
        Action 4:
            - reconcile 2.000.000 for invoice
        Output 4:
            - amount residual on invoice = 1.000.000
        """
        so1 = self._create_so(partner=self.partner_a, price_unit=6000000)

        payment = self._create_account_payment(5000000, so1)
        payment.post()

        so1.action_confirm()

        move_form = Form(self.env['account.move'].with_context(default_type='out_invoice'))
        move_form.partner_id = so1.partner_id
        with move_form.invoice_line_ids.new() as line:
            line.product_id = so1.order_line.product_id
            line.price_unit = 6000000
            line.quantity = 1
            # Removes all existing taxes in the invoice line to no change price total
            line.tax_ids.clear()
        move = move_form.save()
        move.invoice_line_ids.write({'sale_line_ids': [(4, so1.order_line.id)]})
        move.post()

        # Action 1: reconcile 3.000.000 for invoice
        payable_line = payment.move_line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'receivable')
        wizard = self.env['assign.to.invoice.wizard']\
            .with_context(move_id=move.id, line_id=payable_line.id)\
            .create({'amount': 3000000})
        wizard.with_context(move_id=move.id, line_id=payable_line.id).add()

        # Output 1: amount residual on invoice = 3.000.000
        self.assertEqual(move.amount_residual, 3000000)

        # Action 2: reconcile 3.000.000 for invoice
        payable_line = payment.move_line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'receivable')
        wizard = self.env['assign.to.invoice.wizard']\
            .with_context(move_id=move.id, line_id=payable_line.id)\
            .create({'amount': 3000000})

        # Output 2: error
        with self.assertRaises(ValidationError):
            wizard.with_context(move_id=move.id, line_id=payable_line.id).add()

        # Action 3: reconcile 3.000.000 for invoice
        wizard.amount = -3000000
        # Output 3: error
        with self.assertRaises(UserError):
            wizard.with_context(move_id=move.id, line_id=payable_line.id).add()

        # Action 4: reconcile 2.000.000 for invoice
        payable_line = payment.move_line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'receivable')
        wizard = self.env['assign.to.invoice.wizard']\
            .with_context(move_id=move.id, line_id=payable_line.id)\
            .create({'amount': 2000000})
        wizard.with_context(move_id=move.id, line_id=payable_line.id).add()

        # Output 4: amount residual on invoice = 1.000.000
        self.assertEqual(move.amount_residual, 1000000)

    def test_02_reconcile_payment_with_invoice_diff_currency(self):
        """
        Input:
            - Payment:
                - link to SO1
                - amount = 5.000.000 USD
            - Invoice:
                - total = 6.000.000 Euro
        Action 1:
            - reconcile 3.000.000 Euro for invoice
        Output 1:
            - amount residual on invoice = 3.000.000 Euro
        """
        so1 = self._create_so(partner=self.partner_a, price_unit=6000000)

        payment = self._create_account_payment(5000000, so1)
        payment.post()

        so1.action_confirm()

        move_form = Form(self.env['account.move'].with_context(default_type='out_invoice'))
        move_form.partner_id = so1.partner_id
        currency_eur = self.env['res.currency'].search([('name', '=', 'EUR')], limit=1)
        if not currency_eur.active:
            currency_eur.active = True
        move_form.currency_id = currency_eur
        with move_form.invoice_line_ids.new() as line:
            line.product_id = so1.order_line.product_id
            line.quantity = 1
            line.price_unit = 6000000
            # Removes all existing taxes in the invoice line to no change price total
            line.tax_ids.clear()
        move = move_form.save()
        move.invoice_line_ids.write({'sale_line_ids': [(4, so1.order_line.id)]})
        move.post()

        # Action 1: reconcile 3.000.000 EUR for invoice
        payable_line = payment.move_line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'receivable')
        wizard = self.env['assign.to.invoice.wizard']\
            .with_context(move_id=move.id, line_id=payable_line.id)\
            .create({'amount': 3000000})
        wizard.with_context(move_id=move.id, line_id=payable_line.id).add()

        # Output 1: amount residual on invoice = 3.000.000 EUR
        self.assertEqual(move.amount_residual, 3000000)

    def test_03_reconcile_payment_with_invoice_diff_so(self):
        """
        Input:
            - Payment:
                - link to SO1
            - Invoice:
                - link to SO2
        Action 1: reconcile payment with invoice
        Output 1:
            - error
        Action 2: add SO2 to payment, then reconcile payment with invoice
        Output 2:
            - ok
        """
        so1 = self._create_so(partner=self.partner_a, price_unit=6000000)
        so2 = self._create_so(partner=self.partner_a, price_unit=6000000)
        (so1 | so2).action_confirm()

        payment = self._create_account_payment(5000000, so1)
        payment.post()

        move_form = Form(self.env['account.move'].with_context(default_type='out_invoice'))
        move_form.partner_id = so2.partner_id
        with move_form.invoice_line_ids.new() as line:
            line.product_id = so2.order_line.product_id
            line.quantity = 1
            line.price_unit = 6000000
            # Removes all existing taxes in the invoice line to no change price total
            line.tax_ids.clear()
        move = move_form.save()
        move.invoice_line_ids.write({'sale_line_ids': [(4, so2.order_line.id)]})
        move.post()

        # Action 1: reconcile payment with invoice
        # Output 1: error
        payable_line = payment.move_line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'receivable')
        wizard = self.env['assign.to.invoice.wizard']\
            .with_context(move_id=move.id, line_id=payable_line.id)\
            .create({'amount': 3000000})
        with self.assertRaises(UserError):
            wizard.with_context(move_id=move.id, line_id=payable_line.id).add()

        # Action 2: add SO2 to payment, then reconcile payment with invoice
        # Output 2: ok
        payment.sale_order_ids = [(4, so2.id)]
        wizard.with_context(move_id=move.id, line_id=payable_line.id).add()

    def test_04_add_so_to_confirmed_payment(self):
        """
        Input:
            - Payment:
                - link to SO1 link to partner a
                - state = confirmed
                - partner link to partner a
            - SO2 link to partner b
        Action: add SO2 to payment
        Output:
            - error
        """
        so1 = self._create_so(partner=self.partner_a, price_unit=6000000)
        so2 = self._create_so(partner=self.partner_b, price_unit=6000000)
        (so1 | so2).action_confirm()

        payment = self._create_account_payment(5000000, so1)
        payment.post()
        wizard = self.env['add.so.to.payment.wizard']\
            .create({'account_payment_id': payment.id,
                     'sale_order_ids': [(6, 0, so2.ids)],
                     })
        with self.assertRaises(ValidationError):
            wizard.add()

    def test_05_add_so_to_confirmed_payment(self):
        """
        Input:
            - Payment:
                - link to SO1 link to partner a
                - state = confirmed
                - partner link to partner a
            - SO2 link to partner a
        Action: add SO2 to payment
        Output:
            - payment is linked to SO1 and SO2
        """
        so1 = self._create_so(partner=self.partner_a, price_unit=6000000)
        so2 = self._create_so(partner=self.partner_a, price_unit=6000000)
        (so1 | so2).action_confirm()

        payment = self._create_account_payment(5000000, so1)
        payment.post()
        wizard = self.env['add.so.to.payment.wizard']\
            .create({'account_payment_id': payment.id,
                     'sale_order_ids': [(6, 0, so2.ids)],
                     })
        wizard.add()
        self.assertEqual(payment.sale_order_ids, (so1 | so2))
