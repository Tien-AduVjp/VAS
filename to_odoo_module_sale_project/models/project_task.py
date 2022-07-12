from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    odoo_module_version_id = fields.Many2one('odoo.module.version', string='Developed Odoo Module',
                                             domain="[('git_branch_id', '=', git_branch_id)]",
                                             help="The module that have been developed according to this task.\n"
                                             "Note that, if this task is related to a sale order line, the corresponding customer"
                                             " will be able to download the module for his customer portal, only when the related invoice is paid.")

