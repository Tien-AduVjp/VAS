from odoo import fields, models


class WizardL10n_vnC200_s10dn(models.TransientModel):
    _name = 'wizard.l10n_vn.c200_s10dn'
    _inherit = 'wizard.stock.report.common'
    _description = 'Vietnam C200 S10-DN Report Wizard'

    product_id = fields.Many2one('product.product', string="Product", required=True, domain=[('type', '!=', 'service')])
    description = fields.Text(string="Product Description", related='product_id.description_picking', readonly=True)
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', readonly=True)

    def _print_report(self, data):
        data['form'].update(self.read(['warehouse_id', 'product_id', 'location_id', 'description', 'uom_id'])[0])
        res = self.env.ref('to_l10n_vn_stock_reports.act_report_c200_s10dn').report_action(self, data=data)
        return res

