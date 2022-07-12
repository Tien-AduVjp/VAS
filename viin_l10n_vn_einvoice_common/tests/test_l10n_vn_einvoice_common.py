from odoo.addons.to_einvoice_common.tests.test_base import TestBaseEinvoiceCommon
from odoo.tests import tagged, Form
from odoo.exceptions import AccessError


@tagged('external', '-standard')
class TestL10nVnEinvoice(TestBaseEinvoiceCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super(TestL10nVnEinvoice, cls).setUpClass(chart_template_ref=chart_template_ref)
        cls.internal_user = cls.env['res.users'].create({
            'name': 'user_internal',
            'login': 'user_internal@example.viindoo.com',
            'email': 'user_internal@example.viindoo.com',
            'groups_id': [(6, 0, cls.env.ref('base.group_user').ids)],
        })
        cls.user_accountant = cls.env['res.users'].create({
            'name': 'user_accountant',
            'login': 'user_accountant@example.viindoo.com',
            'email': 'user_accountant@example.viindoo.com',
            'groups_id': [(6, 0, cls.env.ref('account.group_account_invoice').ids)],
        })

    def test_action_prepend_vietnamese_description_to_invoice_lines(self):
        invoice_form = Form(self.invoice)
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.name = 'description\nsale'
        invoice_form.save()
        self.invoice.action_prepend_vietnamese_description_to_invoice_lines()
        self.assertEqual(self.invoice.invoice_line_ids[0].name, 'description; sale vi_VN (description; sale)')
        self.assertEqual(self.invoice.invoice_line_ids[2].name, 'line note')
        self.invoice.post()
        self.invoice.action_prepend_vietnamese_description_to_invoice_lines()
        self.assertEqual(self.invoice.invoice_line_ids[0].name, 'description; sale vi_VN (description; sale vi_VN (description; sale))')
        self.assertEqual(self.invoice.invoice_line_ids[2].name, 'line note')

    def test_action_prepend_vietnamese_description_to_invoice_lines_access_rights(self):
        invoice_form = Form(self.invoice)
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.name = 'description\nsale'
        invoice_form.save()
        with self.assertRaises(AccessError):
            self.invoice.with_user(self.internal_user).action_prepend_vietnamese_description_to_invoice_lines()
        self.invoice.with_user(self.user_accountant).action_prepend_vietnamese_description_to_invoice_lines()
        self.assertEqual(self.invoice.invoice_line_ids[0].name, 'description; sale vi_VN (description; sale)')
        self.assertEqual(self.invoice.invoice_line_ids[2].name, 'line note')
