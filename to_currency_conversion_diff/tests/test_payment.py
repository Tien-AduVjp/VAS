from odoo import fields
from odoo.tests import tagged, SavepointCase
from odoo.tools.float_utils import float_compare


@tagged('post_install', '-at_install')
class TestPayment(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPayment, cls).setUpClass()

        cls.partner = cls.env['res.partner'].create({'name': 'partner'})

        cls.currency_eur = cls.env.ref('base.EUR')
        cls.currency_usd = cls.env.ref('base.USD')
        cls.currency_vnd = cls.env.ref('base.VND')
        cls.currency_eur.active = True
        cls.currency_usd.active = True
        cls.currency_vnd.active = True

        cls.rate_eur = cls.env['res.currency.rate'].create({
            'rate': 1.000000,
            'currency_id': cls.currency_eur.id,
            'company_id': cls.env.company.id,
        })
        cls.rate_usd = cls.env['res.currency.rate'].create({
            'rate': 1.528900,
            'currency_id': cls.currency_usd.id,
            'company_id': cls.env.company.id,
        })
        cls.rate_vnd = cls.env['res.currency.rate'].create({
            'rate': 26330.010000,
            'currency_id': cls.currency_vnd.id,
            'company_id': cls.env.company.id,
        })

        # Setup default supported currency for payment.payment_acquirer_transfer
        # Setup default converted currency for payment.payment_acquirer_transfer
        cls.default_payment_acquirer = cls.env.ref('payment.payment_acquirer_transfer')

        cls.default_payment_acquirer.write({
            'supported_currency_map_ids': [
                (0, 0, {
                    'currency_id': cls.currency_eur.id,
                }),
                (0, 0, {
                    'currency_id': cls.currency_usd.id,
                })
            ],
            'default_converted_currency_id': cls.currency_usd.id
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product A',
        })

        # Config diff account
        cls.env.company.write({
            'income_currency_conversion_diff_account_id': cls.env.ref('l10n_generic_coa.%s_cash_diff_income' % cls.env.company.id),
            'expense_currency_conversion_diff_account_id': cls.env.ref('l10n_generic_coa.%s_cash_diff_expense' % cls.env.company.id),
            })

    def test_payment_render_01(self):
        """
        [Functional Test] - TC13

        - Case: Render payment in case:
            + invoice has currency, which not in supported currencies of payment acquirer
            + there is setting for default converted currency of payment acquirer
        - Expected Result:
            + there is currency conversion for payment transaction of this invoice
        """
        # Create invoice
        invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner.id,
                'currency_id': self.currency_vnd.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.product.id,
                        'quantity': 3,
                        'price_unit': 100000,
                    })
                ]
            })

        # Create payment transaction from invoice
        transaction = invoice._create_payment_transaction({
            'acquirer_id': self.default_payment_acquirer.id,
        })

        # Render payment form and check data in payment transaction
        values = {
            'partner_id': invoice.partner_id.id,
            'type': transaction.type,
            'type': 'form',
        }
        self.default_payment_acquirer.with_context(submit_class='btn btn-primary', submit_txt='Pay & Confirm').sudo().render(
            transaction.reference,
            invoice.amount_residual,
            invoice.currency_id.id,
            values=values,
        )

        self.assertTrue(transaction.currency_id == self.currency_vnd)
        self.assertTrue(float_compare(transaction.amount, 300000.00, 2) == 0)
        self.assertTrue(transaction.converted_currency_id == self.currency_usd)
        self.assertTrue(float_compare(transaction.converted_amount, 17.42, 2) == 0)

    def test_payment_render_02(self):
        """
        [Functional Test] - TC14

        - Case: Render payment in case:
            + invoice has currency, which not in supported currencies of payment acquirer
            + there is't setting for default converted currency of payment acquirer
        - Expected Result:
            + there is't currency conversion for payment transaction of this invoice
        """
        # Create invoice
        invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner.id,
                'currency_id': self.currency_vnd.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.product.id,
                        'quantity': 3,
                        'price_unit': 100000,
                    })
                ]
            })
        # Remove default converted currency from payment acquirer
        self.default_payment_acquirer.default_converted_currency_id = False

        # Create payment transaction from invoice
        transaction = invoice._create_payment_transaction({
            'acquirer_id': self.default_payment_acquirer.id,
        })

        # Render payment form and check data in payment transaction
        values = {
            'partner_id': invoice.partner_id.id,
            'type': transaction.type,
            'type': 'form',
        }
        self.default_payment_acquirer.with_context(submit_class='btn btn-primary', submit_txt='Pay & Confirm').sudo().render(
            transaction.reference,
            invoice.amount_residual,
            invoice.currency_id.id,
            values=values,
        )

        self.assertTrue(transaction.currency_id == self.currency_vnd)
        self.assertTrue(float_compare(transaction.amount, 300000.00, 2) == 0)
        self.assertTrue(not transaction.converted_currency_id)
        self.assertTrue(float_compare(transaction.converted_amount, 0.00, 2) == 0)

    def test_payment_render_03(self):
        """
        [Functional Test] - TC15

        - Case: Render payment in case:
            + invoice has currency, which in supported currencies of payment acquirer
            + there is setting for default converted currency of payment acquirer
        - Expected Result:
            + there is't currency conversion for payment transaction of this invoice
        """
        # Create invoice
        invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner.id,
                'currency_id': self.currency_eur.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.product.id,
                        'quantity': 3,
                        'price_unit': 100,
                    })
                ]
            })
        # Remove default converted currency from payment acquirer
        self.default_payment_acquirer.default_converted_currency_id = False

        # Create payment transaction from invoice
        transaction = invoice._create_payment_transaction({
            'acquirer_id': self.default_payment_acquirer.id,
        })

        # Render payment form and check data in payment transaction
        values = {
            'partner_id': invoice.partner_id.id,
            'type': transaction.type,
            'type': 'form',
        }
        self.default_payment_acquirer.with_context(submit_class='btn btn-primary', submit_txt='Pay & Confirm').sudo().render(
            transaction.reference,
            invoice.amount_residual,
            invoice.currency_id.id,
            values=values,
        )

        self.assertTrue(transaction.currency_id == self.currency_eur)
        self.assertTrue(float_compare(transaction.amount, 300.00, 2) == 0)
        self.assertTrue(not transaction.converted_currency_id)
        self.assertTrue(float_compare(transaction.converted_amount, 0.00, 2) == 0)

    def test_payment_render_04(self):
        """
        [Functional Test] - TC16

        - Case: Render payment in case:
            + new currency is added in supported currency map of payment acquirer
            + setting default converted currency of payment acquirer is this new created currency
            + invoice has currency is this new currency
        - Expected Result:
            + there is't currency conversion for payment transaction of this invoice
        """
        # Create new currency and add it into default payment acquirer
        other_currency = self.env['res.currency'].create({'name': 'TES',
                                                          'symbol': 'TES'})

        self.default_payment_acquirer.write({
            'supported_currency_map_ids': [
                (0, 0, {
                    'currency_id': other_currency.id,
                })
            ]
        })
        self.default_payment_acquirer.invalidate_cache()
        self.default_payment_acquirer.default_converted_currency_id = other_currency

        # Create invoice
        invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner.id,
                'currency_id': other_currency.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.product.id,
                        'quantity': 3,
                        'price_unit': 100,
                    })
                ]
            })

        # Create payment transaction from invoice
        transaction = invoice._create_payment_transaction({
            'acquirer_id': self.default_payment_acquirer.id,
        })

        # Render payment form and check data in payment transaction
        values = {
            'partner_id': invoice.partner_id.id,
            'type': transaction.type,
            'type': 'form',
        }
        self.default_payment_acquirer.with_context(submit_class='btn btn-primary', submit_txt='Pay & Confirm').sudo().render(
            transaction.reference,
            invoice.amount_residual,
            invoice.currency_id.id,
            values=values,
        )

        self.assertTrue(transaction.currency_id == other_currency)
        self.assertTrue(float_compare(transaction.amount, 300.00, 2) == 0)
        self.assertTrue(not transaction.converted_currency_id)
        self.assertTrue(float_compare(transaction.converted_amount, 0.00, 2) == 0)

    def test_payment_transaction_01(self):
        """
        [Functional Test] - TC17

        - Case: Complete payment in case:
            + invoice has currency is in supported currencies of payment acquirer
        - Expected Result:
            + there is't additional move lines created for currency conversion difference
        """

        # Create invoice
        invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner.id,
                'currency_id': self.currency_eur.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.product.id,
                        'quantity': 3,
                        'price_unit': 100,
                    })
                ]
            })
        invoice.action_post()

        # Create payment transaction from invoice
        transaction = invoice._create_payment_transaction({
            'acquirer_id': self.default_payment_acquirer.id,
        })

        # Render payment form and check data in payment transaction
        values = {
            'partner_id': invoice.partner_id.id,
            'type': transaction.type,
            'type': 'form',
        }
        self.default_payment_acquirer.with_context(submit_class='btn btn-primary', submit_txt='Pay & Confirm').sudo().render(
            transaction.reference,
            invoice.amount_residual,
            invoice.currency_id.id,
            values=values,
        )

        self.assertTrue(transaction.currency_id == self.currency_eur)
        self.assertTrue(float_compare(transaction.amount, 300.00, 2) == 0)
        self.assertTrue(not transaction.converted_currency_id)
        self.assertTrue(float_compare(transaction.converted_amount, 0.00, 2) == 0)

        # Set transaction done
        transaction._set_transaction_done()

        # Post-process after transaction done
        transaction._post_process_after_done()

        payment = transaction.payment_id

        diff_move_line = payment.line_ids.filtered(
            lambda ml: ml.journal_id  == self.env.company.currency_conversion_diff_journal_id
            )
        self.assertTrue(len(diff_move_line) == 0)
        self.assertTrue(invoice.payment_state == 'paid')

    def test_payment_transaction_02(self):
        """
        [Functional Test] - TC18

        - Case: Complete payment in case:
            + invoice has currency is not in supported currencies of payment acquirer
            + payment amount is greater than required amount
        - Expected Result:
            + there are additional move lines created for currency conversion difference
            + 1 move line record credit for income account
            + 1 move line record debit for receivable account
        """
        self.rate_usd.rate = 26330.010000
        self.rate_vnd.rate = 1.528900
        self.env['res.currency.rate'].flush()
        self.env['res.currency.rate'].invalidate_cache()

        currency_usd_map = self.default_payment_acquirer.supported_currency_map_ids.filtered(lambda sc: sc.currency_id == self.currency_usd)[0]
        currency_usd_map.unlink()
        self.default_payment_acquirer.write({
            'supported_currency_map_ids': [
                (0, 0, {
                    'currency_id': self.currency_vnd.id,
                })
            ],
            'default_converted_currency_id': self.currency_vnd.id
        })

        # Create invoice
        invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner.id,
                'currency_id': self.currency_usd.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.product.id,
                        'quantity': 100,
                        'price_unit': 539000,
                    })
                ]
            })
        invoice.action_post()

        # Create payment transaction from invoice
        transaction = invoice._create_payment_transaction({
            'acquirer_id': self.default_payment_acquirer.id,
        })

        # Render payment form and check data in payment transaction
        values = {
            'partner_id': invoice.partner_id.id,
            'type': transaction.type,
            'type': 'form',
        }
        self.default_payment_acquirer.with_context(submit_class='btn btn-primary', submit_txt='Pay & Confirm').sudo().render(
            transaction.reference,
            invoice.amount_residual,
            invoice.currency_id.id,
            values=values,
        )

        self.assertTrue(transaction.currency_id == self.currency_usd)
        self.assertTrue(float_compare(transaction.amount, 53900000.00, 2) == 0)
        self.assertTrue(transaction.converted_currency_id == self.currency_vnd)
        self.assertTrue(float_compare(transaction.converted_amount, 3130.0, 2) == 0)

        # Set transaction done
        transaction._set_transaction_done()

        # Post-process after transaction done
        transaction._post_process_after_done()

        payment = transaction.payment_id
        diff_move_line = self.env['account.move.line'].search([
            ('payment_id', '=', payment.id),
            ('account_id.internal_type', '=', 'receivable'),
            ]).filtered(
                lambda ml: ml.journal_id  == self.env.company.currency_conversion_diff_journal_id
                )
        self.assertTrue(len(diff_move_line) == 1)

        # In this case payment amount after convert is more than payment transaction amount
        # => we will record credit income and debit receivable
        self.assertTrue(len(diff_move_line.move_id.line_ids) == 2)
        income_move_line = diff_move_line.move_id.line_ids.filtered(
            lambda ml: ml.account_id == self.env.ref('l10n_generic_coa.%s_cash_diff_income' % self.env.company.id)
            )
        receivable_move_line = diff_move_line.move_id.line_ids.filtered(
            lambda ml: ml.account_id == self.env.ref('l10n_generic_coa.%s_receivable' % self.env.company.id)
            )

        self.assertTrue(len(income_move_line) == 1)
        self.assertTrue(len(receivable_move_line) == 1)
        self.assertTrue(float_compare(income_move_line.credit, 0.0, 2) > 0)
        self.assertTrue(float_compare(income_move_line.debit, 0.0, 2) == 0)
        self.assertTrue(float_compare(receivable_move_line.credit, 0.0, 2) == 0)
        self.assertTrue(float_compare(receivable_move_line.debit, 0.0, 2) > 0)

        self.assertTrue(invoice.payment_state == 'paid')

    def test_payment_transaction_03(self):
        """
        [Functional Test] - TC19

        - Case: Complete payment in case:
            + invoice has currency is not in supported currencies of payment acquirer
            + payment amount is less than required amount
        - Expected Result:
            + there are additional move lines created for currency conversion difference
            + 1 move line record debit for expense account
            + 1 move line record credit for receivable account
        """
        self.rate_usd.rate = 26330.010000
        self.rate_vnd.rate = 1.528900
        self.env['res.currency.rate'].flush()
        self.env['res.currency.rate'].invalidate_cache()

        currency_usd_map = self.default_payment_acquirer.supported_currency_map_ids.filtered(lambda sc: sc.currency_id == self.currency_usd)[0]
        currency_usd_map.unlink()
        self.default_payment_acquirer.write({
            'supported_currency_map_ids': [
                (0, 0, {
                    'currency_id': self.currency_vnd.id,
                })
            ],
            'default_converted_currency_id': self.currency_vnd.id
        })

        # Create invoice
        invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner.id,
                'currency_id': self.currency_usd.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.product.id,
                        'quantity': 100,
                        'price_unit': 600000,
                    })
                ]
            })
        invoice.action_post()

        # Create payment transaction from invoice
        transaction = invoice._create_payment_transaction({
            'acquirer_id': self.default_payment_acquirer.id,
        })

        # Render payment form and check data in payment transaction
        values = {
            'partner_id': invoice.partner_id.id,
            'type': transaction.type,
            'type': 'form',
        }
        self.default_payment_acquirer.with_context(submit_class='btn btn-primary', submit_txt='Pay & Confirm').sudo().render(
            transaction.reference,
            invoice.amount_residual,
            invoice.currency_id.id,
            values=values,
        )

        self.assertTrue(transaction.currency_id == self.currency_usd)
        self.assertTrue(float_compare(transaction.amount, 60000000.00, 2) == 0)
        self.assertTrue(transaction.converted_currency_id == self.currency_vnd)
        self.assertTrue(float_compare(transaction.converted_amount, 3484.0, 2) == 0)

        # Set transaction done
        transaction._set_transaction_done()

        # Post-process after transaction done
        transaction._post_process_after_done()

        payment = transaction.payment_id
        diff_move_line = self.env['account.move.line'].search([
            ('payment_id', '=', payment.id),
            ('account_id.internal_type', '=', 'receivable'),
            ]).filtered(
                lambda ml: ml.journal_id  == self.env.company.currency_conversion_diff_journal_id
                )
        self.assertTrue(len(diff_move_line) == 1)

        # In this case payment amount after convert is more than payment transaction amount
        # => we will record debit expense and credit receivable
        self.assertTrue(len(diff_move_line.move_id.line_ids) == 2)
        expense_move_line = diff_move_line.move_id.line_ids.filtered(lambda ml: ml.account_id == self.env.ref('l10n_generic_coa.1_cash_diff_expense'))
        receivable_move_line = diff_move_line.move_id.line_ids.filtered(lambda ml: ml.account_id == self.env.ref('l10n_generic_coa.1_receivable'))

        self.assertTrue(len(expense_move_line) == 1)
        self.assertTrue(len(receivable_move_line) == 1)
        self.assertTrue(float_compare(expense_move_line.credit, 0.0, 2) == 0)
        self.assertTrue(float_compare(expense_move_line.debit, 0.0, 2) > 0)
        self.assertTrue(float_compare(receivable_move_line.credit, 0.0, 2) > 0)
        self.assertTrue(float_compare(receivable_move_line.debit, 0.0, 2) == 0)

        self.assertTrue(invoice.payment_state == 'paid')
