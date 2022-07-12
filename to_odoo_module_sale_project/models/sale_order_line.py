from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_odoo_module_versions(self, uom_precision=None):
        odoo_module_version_ids = super(SaleOrderLine, self).get_odoo_module_versions(uom_precision=uom_precision)
        project_module_version_ids = self.sudo().mapped('task_id.odoo_module_version_id')
        if project_module_version_ids:
            odoo_module_version_ids |= project_module_version_ids
        return odoo_module_version_ids

