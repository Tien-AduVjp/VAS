from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ConfigSection(models.Model):
    _inherit = 'config.section'

    odoo_version_config_ids = fields.One2many('odoo.version.config', 'section_id', readonly=True)

    def write(self, vals):
        name_in_vals = 'name' in vals
        for r in self:
            if name_in_vals and r.name != vals['name'] and r.odoo_version_config_ids:
                raise UserError(_("Modifying section name is not allowed while an Odoo version configuration directive is still referring to it"))

        return super(ConfigSection, self).write(vals)
