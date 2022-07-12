from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('sale_line_ids.task_id.odoo_module_version_id')
    def _compute_odoo_module_version(self):
        super(AccountMoveLine, self)._compute_odoo_module_version()

    def get_odoo_module_versions(self, uom_precision=None):
        odoo_module_version_ids = super(AccountMoveLine, self).get_odoo_module_versions(uom_precision=uom_precision)
        project_module_version_ids = self.sudo().mapped('sale_line_ids.task_id.odoo_module_version_id')
        if project_module_version_ids:
            odoo_module_version_ids |= project_module_version_ids
        return odoo_module_version_ids
