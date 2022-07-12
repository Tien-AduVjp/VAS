from odoo import models, fields, api


class ProductLicenseVersion(models.Model):
    _inherit = 'product.license.version'

    sale_line_ids = fields.Many2many('sale.order.line', 'sale_line_product_license_version_rel', 'product_license_version_id', 'sale_line_id', readonly=True,
                                     string='Sale Lines', help="The sales lines that refer to this license version")
    sale_lines_count = fields.Integer(string='Sale Lines Count', compute='_compute_sale_lines_count')

    def _compute_sale_lines_count(self):
        for r in self:
            r.sale_lines_count = len(r.sale_line_ids.filtered(lambda l: l.state in ['sale', 'done']))

    def action_view_sale_lines(self):
        sale_line_ids = self.mapped('sale_line_ids').filtered(lambda l: l.state in ['sale', 'done'])
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'name': 'Sales Order Lines',
            'res_model': 'sale.order.line',
            'domain':  "[('id', 'in', " + str(sale_line_ids.ids) + ")]"
        }

