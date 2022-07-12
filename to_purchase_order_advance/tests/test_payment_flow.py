from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, tagged
from odoo import fields

from .payment_common import PaymentCommon


@tagged('post_install', '-at_install')
class TestPaymentFlow(PaymentCommon):

    def test_01_reconcile_payment_with_invoice_same_currency(self):
        """
        Input:
            - Payment:
                - link to PO1
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
        po1 = self._create_po(partner=self.partner_a, price_unit=6000000)

        payment = self._create_account_payment(5000000, po1)
        payment.action_post()

        po1.button_confirm()

        move_form = Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.partner_id = po1.partner_id
        move_form.purchase_id = po1
        move_form.invoice_date = fields.Date.today()
        with move_form.invoice_line_ids.edit(0) as line:
            line.quantity = 1
        move = move_form.save()
        move.action_post()

        # Action 1: reconcile 3.000.000 for invoice
        payable_line = payment.line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'payable')
        wizard = self.env['assign.to.invoice.wizard']\
            .with_context(move_id=move.id, line_id=payable_line.id)\
            .create({'amount': 3000000})
        wizard.with_context(move_id=move.id, line_id=payable_line.id).add()

        # Output 1: amount residual on invoice = 3.000.000
        self.assertEqual(move.amount_residual, 3000000)

        # Action 2: reconcile 3.000.000 for invoice
        payable_line = payment.line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'payable')
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
        payable_line = payment.line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'payable')
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
                - link to PO1
                - amount = 5.000.000 USD
            - Invoice:
                - total = 6.000.000 Euro
        Action 1:
            - reconcile 3.000.000 Euro for invoice
        Output 1:
            - amount residual on invoice = 3.000.000 Euro
        """
        po1 = self._create_po(partner=self.partner_a, price_unit=6000000)

        payment = self._create_account_payment(5000000, po1)
        payment.action_post()

        po1.button_confirm()

        move_form = Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.partner_id = po1.partner_id
        move_form.purchase_id = po1
        currency_eur = self.env['res.currency'].search([('name', '=', 'EUR')], limit=1)
        if not currency_eur.active:
            currency_eur.active = True
        move_form.currency_id = currency_eur
        move_form.invoice_date = fields.Date.today()
        with move_form.invoice_line_ids.edit(0) as line:
            line.quantity = 1
        move = move_form.save()
        move.action_post()

        # Action 1: reconcile 3.000.000 EUR for invoice
        payable_line = payment.line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'payable')
        wizard = self.env['assign.to.invoice.wizard']\
            .with_context(move_id=move.id, line_id=payable_line.id)\
            .create({'amount': 3000000})
        wizard.with_context(move_id=move.id, line_id=payable_line.id).add()

        # Output 1: amount residual on invoice = 3.000.000 EUR
        self.assertEqual(move.amount_residual, 3000000)

    def test_03_reconcile_payment_with_invoice_diff_po(self):
        """
        Input:
            - Payment:
                - link to PO1
            - Invoice:
                - link to PO2
        Action 1: reconcile payment with invoice
        Output 1:
            - error
        Action 2: add PO2 to payment, then reconcile payment with invoice
        Output 2:
            - ok
        """
        po1 = self._create_po(partner=self.partner_a, price_unit=6000000)
        po2 = self._create_po(partner=self.partner_a, price_unit=6000000)
        (po1 | po2).button_confirm()

        payment = self._create_account_payment(5000000, po1)
        payment.action_post()

        move_form = Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.partner_id = po2.partner_id
        move_form.purchase_id = po2
        move_form.invoice_date = fields.Date.today()
        with move_form.invoice_line_ids.edit(0) as line:
            line.quantity = 1
        move = move_form.save()
        move.action_post()

        # Action 1: reconcile payment with invoice
        # Output 1: error
        payable_line = payment.line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'payable')
        wizard = self.env['assign.to.invoice.wizard']\
            .with_context(move_id=move.id, line_id=payable_line.id)\
            .create({'amount': 3000000})
        with self.assertRaises(UserError):
            wizard.with_context(move_id=move.id, line_id=payable_line.id).add()

        # Action 2: add PO2 to payment, then reconcile payment with invoice
        # Output 2: ok
        payment.purchase_order_ids = [(4, po2.id)]
        wizard.with_context(move_id=move.id, line_id=payable_line.id).add()

    def test_04_add_po_to_confirmed_payment(self):
        """
        Input:
            - Payment:
                - link to PO1 link to partner a
                - state = confirmed
                - partner link to partner a
            - PO2 link to partner b
        Action: add PO2 to payment
        Output:
            - error
        """
        po1 = self._create_po(partner=self.partner_a, price_unit=6000000)
        po2 = self._create_po(partner=self.partner_b, price_unit=6000000)
        (po1 | po2).button_confirm()

        payment = self._create_account_payment(5000000, po1)
        payment.action_post()
        wizard = self.env['add.po.to.payment.wizard']\
            .create({'account_payment_id': payment.id,
                     'purchase_order_ids': [(6, 0, po2.ids)],
                     })
        with self.assertRaises(ValidationError):
            wizard.add()

    def test_05_add_po_to_confirmed_payment(self):
        """
        Input:
            - Payment:
                - link to PO1 link to partner a
                - state = confirmed
                - partner link to partner a
            - PO2 link to partner a
        Action: add PO2 to payment
        Output:
            - payment is linked to PO1 and PO2
        """
        po1 = self._create_po(partner=self.partner_a, price_unit=6000000)
        po2 = self._create_po(partner=self.partner_a, price_unit=6000000)
        (po1 | po2).button_confirm()

        payment = self._create_account_payment(5000000, po1)
        payment.action_post()
        wizard = self.env['add.po.to.payment.wizard']\
            .create({'account_payment_id': payment.id,
                     'purchase_order_ids': [(6, 0, po2.ids)],
                     })
        wizard.add()
        self.assertEqual(payment.purchase_order_ids, (po1 | po2))
