from odoo.tests.common import Form, tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestAccountTax(Common):
    
    # Add account tax group in tax
    def test_onchange_tax_group_id(self):
        account_tax_repartition_line1 = self.AccountTaxRepartitionLine.create({
            'factor_percent': 100,
            'repartition_type': 'tax',
            'invoice_tax_id': self.account_tax1.id
        })
        account_tax_repartition_line2 = self.AccountTaxRepartitionLine.create({
            'factor_percent': 100,
            'repartition_type': 'tax',
            'refund_tax_id': self.account_tax1.id
        })
        self.account_tax1.write({
            'invoice_repartition_line_ids': [(4, account_tax_repartition_line1.id, 0)],
            'refund_repartition_line_ids': [(4, account_tax_repartition_line2.id, 0)]
        })
        
        account_tax_form = Form(self.account_tax1)
        account_tax_form.tax_group_id = self.account_tax_group1
        account_tax = account_tax_form.save()

        self.assertEqual(account_tax.invoice_repartition_line_ids.vat_ctp_account_id[:1].id,
                        self.account_tax_group1.vat_ctp_account_id.id, "VAT Counterpart Account are not equal")

        self.assertEqual(account_tax.refund_repartition_line_ids.vat_ctp_account_id[:1].id,
                        self.account_tax_group1.vat_ctp_account_id.id, "VAT Counterpart Account are not equal")
