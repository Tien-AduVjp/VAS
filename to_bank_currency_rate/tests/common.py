from datetime import date, datetime

from odoo.tests import SavepointCase, Form


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()

        cls.env.user.groups_id = [(4, cls.env.ref('base.group_multi_currency').id)]

        cls.company_currency = cls.env.company.currency_id
        cls.vnd = cls.env.ref('base.VND')
        cls.vnd.active = True

        # Make currency company to standard currency
        cls.company_currency.rate_ids.unlink()
        cls.create_rate(cls.company_currency, 1, bank=False, exchange_type=False, date='2010-01-01')

        cls.bank_default = cls.env.ref('base.bank_ing')
        cls.bank2 = cls.env.ref('base.bank_bnp')
        cls.bank_no_rate = cls.env['res.bank'].create({
            'name': 'ACB',
            'bic': 'ACBDEF'
            })


        cls.bank_account_company = cls.env['res.partner.bank'].create({
            'acc_number': '1999',
            'partner_id': cls.env.company.id,
            'currency_id': cls.company_currency.id
            })

        cls.default_journal_bank = cls.env.company.bank_journal_ids[:1]
        cls.default_journal_bank.write({
            'bank_account_id': cls.bank_account_company.id,
            })

        cls.env.company.main_currency_bank_id = cls.bank_default
        cls.vnd.rate_ids.unlink()
        cls.create_rate(cls.vnd, 10000, cls.bank_default, 'sell_rate', '2021-05-05', '2021-05-05 08:00:00')
        cls.create_rate(cls.vnd, 15000, cls.bank2, 'sell_rate', '2021-05-05', '2021-05-05 08:00:05')

        cls.create_rate(cls.vnd, 20000, cls.bank_default, 'sell_rate', '2021-07-07', '2021-07-07 08:00:00')
        cls.create_rate(cls.vnd, 25000, cls.bank2, 'sell_rate', '2021-07-07', '2021-07-07 08:00:05')

        cls.create_rate(cls.vnd, 12000, cls.bank_default, 'buy_rate', '2021-05-05', '2021-05-05 09:00:00')
        cls.create_rate(cls.vnd, 17000, cls.bank2, 'buy_rate', '2021-05-05', '2021-05-05 09:00:05')

        cls.create_rate(cls.vnd, 22000, cls.bank_default, 'buy_rate', '2021-07-07', '2021-07-07 09:00:00')
        cls.create_rate(cls.vnd, 27000, cls.bank2, 'buy_rate', '2021-07-07', '2021-07-07 09:00:05')

        cls.create_rate(cls.vnd, 13000, cls.bank_default, 'transfer_rate', '2021-05-05', '2021-05-05 10:00:00')
        cls.create_rate(cls.vnd, 18000, cls.bank2, 'transfer_rate', '2021-05-05', '2021-05-05 10:00:05')

        cls.create_rate(cls.vnd, 23000, cls.bank_default, 'transfer_rate', '2021-07-07', '2021-07-07 10:00:00')
        cls.create_rate(cls.vnd, 28000, cls.bank2, 'transfer_rate', '2021-07-07', '2021-07-07 10:00:05')

    @classmethod
    def create_rate(cls, currency, inverse_rate, bank, exchange_type, date=date.today(), date_create=datetime.now()):
        rate =  cls.env['res.currency.rate'].create({
            'name': date,
            'currency_id': currency.id,
            'inverse_rate': inverse_rate,
            'company_id': cls.env.company.id,
            'bank_id': bank and bank.id,
            'exchange_type': exchange_type,
            })
        rate.flush(['write_date'], rate)
        cls.env.cr.execute("""UPDATE res_currency_rate SET write_date = %s WHERE id = %s""", (date_create, rate.id))
        rate.invalidate_cache(['write_date'], [rate.id])
        return rate

    @classmethod
    def create_invoices(cls, type_invoice, currency, value, date=date.today()):
        product = cls.env.ref('product.product_product_3')
        invoice_form = Form(cls.env['account.move'].with_context(default_move_type=type_invoice))
        invoice_form.currency_id = currency
        invoice_form.invoice_date = date
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = product
            line.quantity = 1
            line.price_unit = value
        invoice = invoice_form.save()
        return invoice, invoice.line_ids.filtered(lambda r: r.product_id == product)

    @classmethod
    def create_payment(cls, type_payment, currency, amount, journal=False, internal_transfer=False, date=date.today()):
        payment_form = Form(cls.env['account.payment'].with_context(default_payment_type=type_payment))
        payment_form.journal_id = journal or cls.default_journal_bank
        payment_form.is_internal_transfer = internal_transfer
        payment_form.currency_id = currency
        payment_form.date = date
        payment_form.amount = amount
        payment = payment_form.save()
        return payment, payment.line_ids[-1:]
