from odoo import models

class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def _load(self, sale_tax_rate, purchase_tax_rate, company):
        """
        Implement this method to set VAT counterpart account for created taxes when load chart template for new company
        """
        res = super(AccountChartTemplate, self)._load(sale_tax_rate, purchase_tax_rate, company)

        # set VAT counterpart account for VAT tax
        vat_taxes = self.env['account.tax'].search([('is_vat', '=', True),
                                                    ('company_id.property_vat_ctp_account_id', '!=', False),
                                                    ('company_id', '=', company.id)])
        for tax in vat_taxes:
            tax.invoice_repartition_line_ids.write({
                'vat_ctp_account_id': tax.company_id.property_vat_ctp_account_id.id
            })
            tax.refund_repartition_line_ids.write({
                'vat_ctp_account_id': tax.company_id.property_vat_ctp_account_id.id
            })
        return res
