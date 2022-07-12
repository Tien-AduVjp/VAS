from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """
    This method modify the income report to include Financial Income
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    odoo_version_ids = env['odoo.version'].search([])
    for odoo_version_id in odoo_version_ids:
        git_branch_ids = env['git.branch'].search([('name', '=', odoo_version_id.name)])
        if git_branch_ids:
            git_branch_ids.write({'odoo_version_id': odoo_version_id.id})

