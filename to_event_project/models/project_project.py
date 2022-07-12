from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    event_id = fields.Many2one('event.event', string='Event', groups='event.group_event_user')
