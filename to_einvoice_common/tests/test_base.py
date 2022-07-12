from datetime import datetime
from unittest.mock import patch
from odoo import fields
from odoo.addons.account.tests.account_test_savepoint import AccountTestInvoicingCommon
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import mute_logger


class TestBaseEinvoiceCommon(AccountTestInvoicingCommon):
    
    def patch_date_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.today', return_value=today)
    
    def patch_date_context_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.context_today', return_value=today)
    
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.registry.enter_test_mode(cls.cr)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.company_data['company']
        cls.partner_a.write({
            'company_type': 'company',
            'street': '31 Bạch Đằng',
            'country_id': cls.env.ref('base.us'),
            'vat': '123456789',
            'email': 'khaihoan@example.viindoo.com',
            'city': 'Hải Phòng',
            'phone': '0978654321',
        })
        lang_vi_VN = cls.env.ref('base.lang_vi_VN')
        lang_vi_VN_code = lang_vi_VN.code
        if not lang_vi_VN.active:
            with mute_logger('odoo.tools.translate', 'odoo.addons.base.models.ir_translation'):
                cls.env['base.language.install'].create({'lang': lang_vi_VN_code}).lang_install()
        translation_vi_VN_product_a_name = cls.env['ir.translation'].search(
            [('name', '=', 'product.product,name'), ('res_id', '=', cls.product_a.id), ('lang', '=', lang_vi_VN_code)])
        translation_vi_VN_product_a_name.write({'src': 'product_a_vi_VN'})
        cls.product_a.write({
            'description_sale': 'description\nsale',
            'default_code': 'default_code_product_a'
        })
        cls.product_b.write({
            'default_code': 'default_code_product_b',
            'taxes_id': [(6, 0, cls.tax_sale_b.ids)],
        })
        cls.env['ir.translation'].create([{
            'name': 'product.template,description_sale',
            'res_id': cls.product_a.product_tmpl_id.id,
            'lang': lang_vi_VN_code,
            'src': 'description\nsale',
            'value': 'description\nsale vi_VN',
            'type': 'model',
        }, {
            'name': 'product.template,name',
            'res_id': cls.product_a.product_tmpl_id.id,
            'lang': lang_vi_VN_code,
            'src': 'product_a',
            'value': 'product_a_vi_VN',
            'type': 'model',
        }])
        cls.config = cls.env['res.config.settings']
        cls.default_values = cls.config.default_get(list(cls.config.fields_get()))
        cls.default_values.update({
            'sinvoice_exchange_file_as_attachment': True,
            'sinvoice_representation_file_as_attachment': True,
        })
        cls.config.create(cls.default_values).execute()
        cls.bank = cls.env["res.bank"].create(
            {
                "name": "Ngân hàng ACB",
                "bic": "khaihoan",
            }
        )
        cls.bank_account = cls.env["res.partner.bank"].create(
            {
                "acc_number": "zuiqua",
                "bank_id": cls.bank.id,
                "partner_id": cls.company.partner_id.id,
            }
        )
        cls.company.write({
            'vat': '0201994665',
            'street': 'Kỳ Sơn',
            'phone': '0918777888',
            'website': 'viindoo.com',
            'email': 'khaihoan@example.viindoo.com',
            'einvoice_issue_earliest_invoice_first': False,
        })
        cls.company_data['default_journal_bank'].write({
            'bank_account_id': cls.bank_account.id,
            'einvoice_display_bank_account': True
        })
        cls.invoice_date = fields.Date.to_date('2021-09-01')

    @classmethod
    def tearDownClass(cls):
        cls.registry.leave_test_mode()
        super().tearDownClass()

    @classmethod
    def create_invoice(cls, type='out_invoice', partner=None, invoice_date=None, post=True):
        invoice_date = invoice_date or fields.Date.today()
        invoice = cls.init_invoice(type, partner=partner, invoice_date=invoice_date)
        if post:
            invoice.post()
        return invoice

    @classmethod
    def create_payment(cls, **custom_vals):
        vals = {
            'amount': 0,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': cls.partner_a.id,
            'currency_id': cls.company_data['currency'].id,
            'payment_method_id': cls.env.ref('account.account_payment_method_manual_in').id,
            'journal_id': cls.company_data['default_journal_bank'].id,
        }
        vals.update(custom_vals)
        payment = cls.env['account.payment'].create(vals)
        payment.post()
        return payment

    def check_issue_einvoice_raise_excep(self):
        with self.assertRaises(UserError, msg="Issue vendor bill"):
            self.create_invoice('in_invoice').issue_einvoices()
        with self.assertRaises(ValidationError, msg="Issue invoice not posted"):
            with self.env.cr.savepoint():
                self.invoice.button_draft()
                self.invoice.issue_einvoices()
        with self.assertRaises(ValidationError, msg="Partner have no street"):
            with self.env.cr.savepoint():
                self.partner_a.write({'street': ''})
                self.invoice.issue_einvoices()
        with self.assertRaises(ValidationError, msg="Partner have no country"):
            with self.env.cr.savepoint():
                self.partner_a.write({'country_id': False})
                self.invoice.issue_einvoices()
        with self.assertRaises(ValidationError, msg="Company partner have no VAT"):
            with self.env.cr.savepoint():
                self.partner_a.write({'country_id': self.env.ref('base.vn').id})
                self.partner_a.write({'vat': ''})
                self.invoice.issue_einvoices()
        with self.assertRaises(ValidationError, msg="Company have no street"):
            with self.env.cr.savepoint():
                self.company.write({'street': ''})
                self.invoice.issue_einvoices()
        with self.assertRaises(UserError, msg="Invoice date earlier than the company's E-Invoice Start Date"):
            with self.env.cr.savepoint():
                self.invoice.invoice_date = fields.Date.to_date('2021-07-30')
                self.invoice.issue_einvoices()
        with self.assertRaises(UserError, msg="Issue earliest invoice"):
            with self.env.cr.savepoint():
                self.company.write({'einvoice_issue_earliest_invoice_first': True})
                earlier_move = self.invoice._find_earliest_unissued_customer_invoice(
                    self.company.sinvoice_start)
                if not earlier_move:
                    self.init_invoice('out_invoice', invoice_date=fields.Date.to_date('2021-08-02')).post()
                self.invoice.issue_einvoices()
        with self.assertRaises(UserError, msg="Issue line no tax"):
            with self.env.cr.savepoint():
                invoice = self.create_invoice(post=False)
                invoice.invoice_line_ids[0].write({'tax_ids': [(5, 0, 0)]})
                invoice.action_post()
                invoice.issue_einvoices()
        with self.assertRaises(UserError, msg="Issue line more than one tax"):
            with self.env.cr.savepoint():
                invoice = self.create_invoice(post=False)
                invoice.invoice_line_ids[0].write({'tax_ids': [(6, 0, (self.tax_purchase_a + self.tax_purchase_b).ids)]})
                invoice.post()
                invoice.issue_einvoices()
