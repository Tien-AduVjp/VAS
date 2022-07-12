from odoo import models, fields


class WizardL10n_vnC200_s11dn(models.TransientModel):
    _name = 'wizard.l10n_vn.c200_s11dn'
    _inherit = 'wizard.stock.report.common'
    _description = 'Vietnam C200 S11-DN Report Wizard'

    product_categ_id = fields.Many2one('product.category', string='Product Category', help="Select a category to limit data to the category. Leave it"
                                       " empty to ignore this limit")

    def _print_report(self, data):
        data['form'].update(self.read(['warehouse_id', 'location_id', 'company_id', 'product_categ_id'])[0])
        return self.env.ref('to_l10n_vn_stock_reports.act_report_c200_s11dn').report_action(self, data=data)
