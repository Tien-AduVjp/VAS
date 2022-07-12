from odoo import fields, models


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    project_id = fields.Many2one('project.project', string='Project', tracking=True,
                                 help="If specified, it will be the default project for the tickets of this team.")

