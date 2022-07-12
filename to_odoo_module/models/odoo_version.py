from odoo import models, fields


class OdooVersion(models.Model):
    _inherit = 'odoo.version'

    odoo_module_versions = fields.One2many('odoo.module.version', 'odoo_version_id', string='Odoo Module Versions', readonly=True, auto_join=True)

    # value of this field is computed in the odoo.module model, then we set this field as readonly
    odoo_module_ids = fields.Many2many('odoo.module', 'odoo_module_odoo_version_rel', 'version_id', 'module_id',
                                       string='Odoo Modules', readonly=True)
