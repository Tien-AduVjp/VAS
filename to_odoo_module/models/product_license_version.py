from odoo import models, fields


class ProductLicenseVersion(models.Model):
    _inherit = 'product.license.version'

    odoo_module_version_ids = fields.One2many('odoo.module.version', 'license_version_id', string='Odoo Module Versions', readonly=True)
    odoo_module_versions_count = fields.Integer(string='Module Versions Count', compute='_compute_odoo_module_versions_count')

    def _compute_odoo_module_versions_count(self):
        files_data = self.env['odoo.module.version'].read_group([('license_version_id', 'in', self.ids)], ['license_version_id'], ['license_version_id'])
        mapped_data = dict([(it['license_version_id'][0], it['license_version_id_count']) for it in files_data])
        for r in self:
            r.odoo_module_versions_count = mapped_data.get(r.id, 0)
