from odoo import fields, models


class WizardL10n_vnStock_inout(models.TransientModel):
    _name = 'wizard.l10n_vn.stock_inout'
    _inherit = 'wizard.stock.report.common'
    _description = 'Vietnam C200 Stock In/Out Report Wizard'

    type = fields.Selection([
        ('in', 'In'),
        ('out', 'Out')
    ], string="Type", required=True, default='in')

    def _print_report(self, data):
        data['form'].update(self.read(['warehouse_id', 'location_id', 'type'])[0])
        return self.env.ref('to_l10n_vn_stock_reports.act_report_stock_inout').report_action(self, data=data)
