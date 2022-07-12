from odoo import api, models


class ProductTemplateCostStructure(models.AbstractModel):
    _name = 'report.to_mrp_account.product_template_cost_structure'
    _description = 'Product Template Cost Structure Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        productions = self.env['mrp.production'].search([('product_id', 'in', docids), ('state', '=', 'done')])
        lines = self.env['report.to_mrp_account.mrp_cost_structure'].get_report_lines(productions)
        return {'lines': lines}
