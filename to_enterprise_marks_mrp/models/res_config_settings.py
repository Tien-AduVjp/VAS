from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_to_mrp_mps = fields.Boolean("Master Production Schedule (MPS)",
                                       help="Enable master production scheduling with forecast."
                                       " This will install the module Master Production Schedule (aka to_mrp_mps)")
    module_to_mrp_workorder = fields.Boolean(string='Module MRP Workorder')

    @api.onchange('group_mrp_routings')
    def _onchange_group_mrp_routings(self):
        # group_mrp_routings
        if self.group_mrp_routings:
            self.module_to_mrp_workorder = True
        # if 'to_mrp_workorder' is already installed, we don't uninstall it based on the group_mrp_routings
        elif not self.env['ir.module.module'].search([('name', '=', 'to_mrp_workorder'), ('state', '=', 'installed')]):
            self.module_to_mrp_workorder = False
