from odoo.tests.common import Form
from odoo.tests import tagged
from odoo.addons.account.tests.account_test_savepoint import AccountTestInvoicingCommon


@tagged('post_install', '-at_install')
class TestAccountMove(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.invoice = cls.init_invoice('out_invoice')

    def test_00_channge_partner(self):
        # When user change partner_id in Form,invoice_line will change partner_id
        move_form = Form(self.invoice)
        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.delegation_partner_id = self.partner_b
        move_form.save()
        self.assertEqual(self.invoice.invoice_line_ids[0].partner_id, self.partner_b.commercial_partner_id,
                         "to_account_delegation_partner: _onchange_partner_id not worked")
        self.assertEqual(self.invoice.invoice_line_ids[1].partner_id, self.partner_a.commercial_partner_id,
                         "to_account_delegation_partner: _onchange_partner_id not worked")

    def test_01_change_delegation_partner(self):
        # When user change delegation_partner_id in Form,invoice_line will change partner_id
        move_form = Form(self.invoice)
        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.delegation_partner_id = self.partner_b
        move_form.partner_id = self.partner_b
        move_form.save()

        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.delegation_partner_id = self.partner_a
        move_form.save()
        self.assertEqual(self.invoice.invoice_line_ids[0].partner_id, self.partner_a.commercial_partner_id,
                         "to_account_delegation_partner: _onchange_delegation_partner not worked")

    def test_02_change_delegation_partner_when_delete(self):
        # user chose delegation_partner_id, then delete delegation_partner_id
        # on invoice_line, Partner will be Customer of account move
        move_form = Form(self.invoice)
        move_form.partner_id = self.partner_a
        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.delegation_partner_id = self.partner_b
        move_form.save()
        partner_null = self.env['res.partner']
        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.delegation_partner_id = partner_null
        move_form.save()
        self.assertEqual(self.invoice.invoice_line_ids[0].partner_id, self.partner_a.commercial_partner_id,
                         "to_account_delegation_partner: _onchange_delegation_partner not worked")
