from odoo import models, fields


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    color = fields.Integer(string='Color in Kanban',help="Color shown in kanban view", default=0)
