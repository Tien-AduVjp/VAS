from datetime import datetime
from unittest.mock import patch

from odoo import fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import Form
from odoo.tools.misc import mute_logger
from odoo.exceptions import UserError, ValidationError


class TestBaseEinvoiceCommon(AccountTestInvoicingCommon):

    def patch_date_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.context_today', return_value=today)

    def patch_date_context_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.context_today', return_value=today)

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.registry.enter_test_mode(cls.cr)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True, no_reset_password=True))
        cls.company = cls.company_data['company']
        cls.payment_method_manual = cls.env.ref('account.account_payment_method_manual_in')
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
        cls.product_a_b = cls.env['product.product'].create({
            'name': 'product_c',
            'uom_id': cls.env.ref('uom.product_uom_dozen').id,
            'lst_price': 200.0,
            'standard_price': 160.0,
            'property_account_income_id': cls.copy_account(cls.company_data['default_account_revenue']).id,
            'property_account_expense_id': cls.copy_account(cls.company_data['default_account_expense']).id,
            'taxes_id': [(6, 0, (cls.tax_sale_a + cls.tax_sale_b).ids)],
            'supplier_taxes_id': [(6, 0, (cls.tax_purchase_a + cls.tax_purchase_b).ids)],
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
            'einvoice_exchange_file_as_attachment': True,
            'einvoice_representation_file_as_attachment': True,
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
        cls.template = cls.env.ref('l10n_vn_edi.einvoice_template_01GTKT0_001')
        cls.einvoice_service = cls.env['einvoice.service'].sudo().search([('module_id', '=', cls.env.ref('base.module_viin_l10n_vn_accounting_sinvoice').id),
                                                                   ('api_version', '=', 'v1')], limit=1)
        cls.einvoice_service.sudo().write({'company_id': cls.company.id})
        serial = cls.env['account.einvoice.serial'].search([('name', '=', 'AA/20E')], limit=1)
        if not serial:
            serial = cls.env['account.einvoice.serial'].create([{
                'name': 'AA/20E',
                'einvoice_service_id': cls.einvoice_service.id,
                'template_id': cls.template.id
            }])
        cls.serial = serial

    @classmethod
    def tearDownClass(cls):
        if cls.registry.test_cr != None:
            cls.registry.leave_test_mode()
        super().tearDownClass()

    def create_payment(self, invoice):
        pmt_wizard = self.env['account.payment.register'].with_context(active_model='account.move',
                                                                       active_ids=invoice.ids).create([{
            'amount': invoice.amount_total,
            'payment_date': invoice.date,
            'journal_id': self.company_data['default_journal_bank'].id,
            'payment_method_id': self.payment_method_manual.id,
        }])
        return pmt_wizard._create_payments()

    def check_issue_einvoice_raise_excep(self):
        with self.assertRaises(UserError, msg="Issue vendor bill"):
            self.init_invoice('in_invoice', invoice_date=fields.Date.today(), products=self.product_a,
                              post=True).issue_einvoices()
        with self.assertRaises(UserError, msg="Issue invoice not posted"):
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
                    self.company.einvoice_service_id.start_date)
                if not earlier_move:
                    self.init_invoice('out_invoice', invoice_date=fields.Date.to_date('2021-08-02'),
                                      products=self.product_a + self.product_b).action_post()
                self.invoice.issue_einvoices()
        with self.assertRaises(UserError, msg="Issue line no tax"):
            with self.env.cr.savepoint():
                invoice = self.init_invoice('out_invoice', invoice_date=fields.Date.today(), products=self.product_a)
                invoice.invoice_line_ids[0].write({'tax_ids': [(5, 0, 0)]})
                invoice.action_post()
                invoice.issue_einvoices()
        with self.assertRaises(UserError, msg="Issue line more than one tax"):
            with self.env.cr.savepoint():
                invoice = self.init_invoice('out_invoice', invoice_date=fields.Date.today(), products=self.product_a_b,
                                            post=True)
                invoice.issue_einvoices()
