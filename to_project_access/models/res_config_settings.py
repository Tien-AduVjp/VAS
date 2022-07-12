from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    project_user_full_access_rights = fields.Boolean(string='Enable Full Access Rights for Project Manager', readonly=False,
                                related='company_id.project_user_full_access_rights')
