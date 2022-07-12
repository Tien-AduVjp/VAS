from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_license_version_ids = fields.Many2many('product.license.version', 'sale_order_product_license_version_rel', 'sale_order_id', 'product_license_version_id',
                                                   string='Licenses', compute='_compute_product_license_versions', store=True, help="The license version(s) that you want to license for the product sold.")
    product_license_versions_count = fields.Integer(string='Product Licenses Count', compute='_compute_product_license_versions_count')

    @api.depends('order_line', 'order_line.product_license_version_ids')
    def _compute_product_license_versions(self):
        for r in self:
            r.product_license_version_ids = [(6, 0, r.mapped('order_line.product_license_version_ids').ids)]

    @api.depends('product_license_version_ids')
    def _compute_product_license_versions_count(self):
        for r in self:
            r.product_license_versions_count = len(r.product_license_version_ids)

    def action_view_license_versions(self):
        license_version_ids = self.mapped('product_license_version_ids')

        action = self.env['ir.actions.act_window']._for_xml_id('to_product_license.product_license_version_action')

        # choose the view_mode accordingly
        licenses_count = len(license_version_ids)
        if licenses_count != 1:
            action['domain'] = "[('id', 'in', " + str(license_version_ids.ids) + ")]"
        elif licenses_count == 1:
            res = self.env.ref('to_product_license.product_license_version_view_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = license_version_ids.id
        return action

    def action_refresh_for_licenses(self):
        self.order_line._refresh_for_licenses()
