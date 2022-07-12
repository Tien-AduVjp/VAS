import datetime
from odoo.tests import SavepointCase, tagged

@tagged('post_install', '-at_install')
class TestWalletCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(SavepointCase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.currency_vnd = cls.env.ref('base.VND')
        cls.currency_usd = cls.env.ref('base.USD')
        cls.currency_eur = cls.env.ref('base.EUR')

        cls.current_year = datetime.date.today().year

        # Base currency (rate=1): EUR
        # Company currency: USD
        Rate = cls.env['res.currency.rate']
        cls.currency_vnd.rate_ids = Rate.create({
            'name': datetime.date(cls.current_year - 1, 1, 1),
            'rate': 25000,
            'currency_id': cls.currency_vnd.id
        })
        cls.currency_usd.rate_ids = Rate.create([{
            'name': datetime.date(cls.current_year - 1, 1, 1),
            'rate': 1.1,
            'currency_id': cls.currency_usd.id
        }, {
            'name': datetime.date(cls.current_year + 1, 1, 1),
            'rate': 1.2,
            'currency_id': cls.currency_usd.id
        }])

        cls.company = cls.env['res.partner'].create({
            'name': 'Company',
            'company_type': 'company'
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Ngoc',
            'parent_id': cls.company.id
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product',
            'type': 'service'
        })
        cls.bank_journal_usd = cls.env['account.journal'].create({
            'name': 'Bank USD',
            'type': 'bank',
            'code': 'BNK0123456789',
            'currency_id': cls.currency_usd.id
        })
        cls.account_payment_method_manual_in = cls.env.ref('account.account_payment_method_manual_in')
        cls.product_category_all = cls.env.ref('product.product_category_all')
        cls.account_income = cls.product_category_all.property_account_income_categ_id

        cls.account_112 = cls.env['account.account'].create({
            'name': 'Tien gui ngan hang',
            'code': 112001,
            'user_type_id': cls.env.ref('account.data_account_type_liquidity').id
        })
        cls.account_131 = cls.env['account.account'].create({
            'name': 'Phai thu cua KH',
            'code': 131001,
            'user_type_id': cls.env.ref('account.data_account_type_receivable').id,
            'reconcile': True
        })
        cls.acquirer_wire_transfer = cls.env.ref('payment.payment_acquirer_transfer')

    @classmethod
    def create_payment(cls, **custom_vals):
        vals = {
            'amount': 0,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': cls.partner.id,
            'payment_method_id': cls.account_payment_method_manual_in.id,
            'journal_id': cls.bank_journal_usd.id,
            'payment_date': datetime.date(cls.current_year - 1, 1, 1)
        }
        vals.update(custom_vals)
        payment = cls.env['account.payment'].create(vals)
        payment.post()
        return payment

    @classmethod
    def create_invoice(cls, custom_vals={}, custom_line_vals_list=[], post_invoice=True):
        line_vals_list = []
        for custom_line_vals in custom_line_vals_list:
            line_vals = {
                'product_id': cls.product.id,
                'name': cls.product.name,
                'price_unit': 0,
                'account_id': cls.account_income.id
            }
            line_vals.update(custom_line_vals)
            line_vals_list.append(line_vals)
        vals = {
            'type': 'out_invoice',
            'partner_id': cls.partner.id,
            'invoice_line_ids': [(0, 0, vals) for vals in line_vals_list],
            'date': datetime.date(cls.current_year - 1, 1, 1)
        }
        vals.update(custom_vals)
        invoice = cls.env['account.move'].create(vals)
        if post_invoice:
            invoice.action_post()
        return invoice