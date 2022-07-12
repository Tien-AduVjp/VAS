from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    project_user_full_access_rights = fields.Boolean(string='Enable Full Access Rights for Project Manager', default=False,
             help="""Default value for a newly created project to grant full access rights
                    for the project manager to the project.""")
