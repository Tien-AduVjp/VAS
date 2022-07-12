from odoo import models, api


class ReportPickingOperation(models.AbstractModel):
    _name = 'report.to_l10n_vn_picking_operation.report_picking_operation'
    _description = "Vietnam Report Picking Operation"

    @api.model
    def _get_report_values(self, docids, data=None):
        picking_ids = self.env['stock.picking'].search([('id', 'in', docids)])
        return {
            'doc_model': 'stock.picking',
            'doc_ids': docids,
            'docs': picking_ids,
            }
