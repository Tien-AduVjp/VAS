from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.project'

    odoo_module_version_ids = fields.Many2many('odoo.module.version', 'odoo_module_version_project_rel', 'project_id', 'odoo_module_version_id',
                                               string='Odoo Modules', help="The modules that have been developed for this project.")
    odoo_module_versions_count = fields.Integer(string='Odoo Module Versions Count', compute='_compute_odoo_module_versions')

    def _compute_odoo_module_versions(self):
        for r in self:
            r.odoo_module_versions_count = len(r.odoo_module_version_ids)
