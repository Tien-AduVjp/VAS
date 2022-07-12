from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_license_version_ids = fields.Many2many('product.license.version', 'product_tmpl_product_license_version_rel', 'product_tmpl_id', 'product_license_version_id',
                                                   compute='_compute_product_license_version_ids', inverse='_set_product_license_version_ids', store=True, copy=False,
                                                   string='License Versions')

    product_license_ids = fields.Many2many('product.license', 'product_tmpl_product_license_rel', 'product_tmpl_id', 'product_license_id', string='Licenses',
                                           compute='_compute_product_tmpl_licenses', store=True, copy=False)

    product_licenses_count = fields.Integer(string='Licenses Count', compute='_compute_product_licenses_count', store=True)

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        return super(ProductTemplate, self.with_context(do_not_override_product_license_version_ids=True)).create(vals_list)

    @api.depends('product_variant_ids', 'product_variant_ids.product_license_version_ids')
    def _compute_product_license_version_ids(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            # do not compute upon creation of templates
            if self._context.get('do_not_override_product_license_version_ids', False):
                product_license_versions = template.product_license_version_ids
            else:
                product_license_versions = template.product_variant_ids.mapped('product_license_version_ids')
            template.product_license_version_ids = product_license_versions
        for template in (self - unique_variants):
            template.product_license_version_ids = False

    def _set_product_license_version_ids(self):
        for r in self:
            if len(r.product_variant_ids) == 1:
                r.product_variant_ids.product_license_version_ids = [(6, 0, r.product_license_version_ids.ids)]

    @api.depends('product_license_version_ids', 'product_license_version_ids.license_id')
    def _compute_product_tmpl_licenses(self):
        for r in self:
            r.product_license_ids = r.product_license_version_ids.mapped('license_id')

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
