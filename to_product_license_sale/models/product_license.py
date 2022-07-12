from odoo import models, fields, api


class ProductLicense(models.Model):
    _inherit = 'product.license'

    sale_lines_count = fields.Integer(string='Sale Lines Count', compute='_compute_sale_lines_count')

    def _compute_sale_lines_count(self):
        for r in self:
            r.sale_lines_count = len(r.mapped('product_license_version_ids.sale_line_ids').filtered(lambda l: l.state in ['sale', 'done']))

    def action_view_sale_lines(self):
        sale_line_ids = self.mapped('product_license_version_ids.sale_line_ids').filtered(lambda l: l.state in ['sale', 'done'])
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'name': 'Sales Order Lines',
            'res_model': 'sale.order.line',
            'domain': "[('id', 'in', " + str(sale_line_ids.ids) + ")]"
        }

