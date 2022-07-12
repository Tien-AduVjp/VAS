from odoo import models, fields


class Task(models.Model):
    _inherit = 'project.task'

    color_stage = fields.Integer(string='Color in Kanban', related='stage_id.color',
                                 help="This will help us to quick identify stage of project tasks in Kanban view")
