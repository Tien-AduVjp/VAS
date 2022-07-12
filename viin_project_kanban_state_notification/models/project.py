from odoo import models,fields

class Project(models.Model):
    _inherit = 'project.project'

    kanban_state_notification = fields.Boolean(string='Kanban State Notification', default=True,
                                    help='Uncheck this field to turn off notifications to the project manager when kanban state of some tasks were changed')
