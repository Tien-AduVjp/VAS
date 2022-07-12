from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    odoo_version_ids = fields.Many2many('odoo.version', 'product_template_odoo_version_rel', 'product_tmpl_id', 'odoo_version_id', string='Odoo Versions',
                                        compute='_compute_odoo_version_ids', store=True)

    odoo_versions_count = fields.Integer(string='Odoo Versions Count', compute='_compute_odoo_versions_count')

    @api.depends('product_variant_ids', 'product_variant_ids.odoo_version_ids')
    def _compute_odoo_version_ids(self):
        for r in self:
            r.odoo_version_ids = r.product_variant_ids.mapped('odoo_version_ids').ids

    def _compute_odoo_versions_count(self):
        for r in self:
            r.odoo_versions_count = len(r.odoo_version_ids)

    def action_view_odoo_versions(self):
        odoo_version_ids = self.mapped('odoo_version_ids')
        action = self.env.ref('to_odoo_version.odoo_version_action')
        result = action.read()[0]

        odoo_versions_count = len(odoo_version_ids)
        if odoo_versions_count != 1:
            result['domain'] = "[('id', 'in', " + str(odoo_version_ids.ids) + ")]"
        elif odoo_versions_count == 1:
            res = self.env.ref('to_odoo_version.odoo_version_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = odoo_version_ids.id
        return result

