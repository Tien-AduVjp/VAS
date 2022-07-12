from odoo import models

class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def _load(self, sale_tax_rate, purchase_tax_rate, company):
        """
        Implement this method to set VAT counterpart account for created taxes when load chart template for new company
        """
        res = super(AccountChartTemplate, self)._load(sale_tax_rate, purchase_tax_rate, company)
        
        vat_tax_groups = self.env['account.tax.group'].search([('is_vat', '=', True)])
        # TODO will use property field for this case to setting up VAT counterpart account for each company
        # and we will search account based on company
        vat_counterpart_account = self.env['account.account']._get_vat_counterpart_account(company)
        if vat_counterpart_account:
            vat_tax_groups.sudo().write({
                'vat_ctp_account_id': vat_counterpart_account.id
            })
        # set VAT counterpart account for VAT tax
        vat_taxes = self.env['account.tax'].search([('is_vat', '=', True),
                                                    ('tax_group_id.vat_ctp_account_id', '!=', False),
                                                    ('company_id', '=', company.id)])
        for tax in vat_taxes:
            tax.invoice_repartition_line_ids.write({
                'vat_ctp_account_id': tax.tax_group_id.vat_ctp_account_id.id
            })
            tax.refund_repartition_line_ids.write({
                'vat_ctp_account_id': tax.tax_group_id.vat_ctp_account_id.id
            })
        return res
