from odoo import models, api

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    @api.model
    def _update_vat_counterpart_account_for_localization(self):
        vn_chart_template = self.env.ref('l10n_vn.vn_template', False)
        if vn_chart_template:
            vn_companies = self.env['res.company'].search([('chart_template_id', '=', vn_chart_template.id)])
            for company in vn_companies:
                vat_tax_groups = self.env['account.tax.group'].search([('is_vat', '=', True)])
                # TODO will use property field for this case to setting up VAT counterpart account for each company
                vat_counterpart_account = self.env['account.account']._get_vat_counterpart_account(company)
                if vat_counterpart_account:
                    vat_tax_groups.sudo().write({
                        'vat_ctp_account_id': vat_counterpart_account.id
                    })
                
                vat_taxes = self.env['account.tax'].search([('is_vat', '=', True),
                                                            ('tax_group_id.vat_ctp_account_id', '!=', False),
                                                            ('company_id', '=', company.id)])
                for tax in vat_taxes.sudo():
                    tax.invoice_repartition_line_ids.write({
                        'vat_ctp_account_id': tax.tax_group_id.vat_ctp_account_id.id
                    })
                    tax.refund_repartition_line_ids.write({
                        'vat_ctp_account_id': tax.tax_group_id.vat_ctp_account_id.id
                    })
