from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_license_version_ids = fields.Many2many('product.license.version', 'product_product_product_license_version_rel', 'product_id', 'product_license_version_id',
                                                   string='License Versions', copy=False)
    product_license_ids = fields.Many2many('product.license', 'product_product_product_license_rel', 'product_id', 'product_license_id', string='Licenses',
                                           compute='_compute_product_licenses', store=True, copy=False)

    product_licenses_count = fields.Integer(string='Licenses Count', compute='_compute_product_licenses_count', store=True)

    @api.depends('product_license_version_ids')
    def _compute_product_licenses(self):
        for r in self:
            r.product_license_ids = r.product_license_version_ids.mapped('license_id')

    @api.depends('product_license_ids')
    def _compute_product_licenses_count(self):
        for r in self:
            r.product_licenses_count = len(r.product_license_ids)

    def action_view_product_licenses(self):
        license_ids = self.mapped('product_license_ids')

        action = self.env['ir.actions.act_window']._for_xml_id('to_product_license.product_license_action')

        # choose the view_mode accordingly
        licenses_count = len(license_ids)
        if licenses_count != 1:
            action['domain'] = "[('id', 'in', " + str(license_ids.ids) + ")]"
        elif licenses_count == 1:
            res = self.env.ref('to_product_license.product_license_view_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = license_ids.id
        return action
