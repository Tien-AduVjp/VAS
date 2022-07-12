from odoo import fields, models

class EventTrack(models.Model):
    _inherit = 'event.track'

    slide_channel_id = fields.Many2one('slide.channel', string='Course', related='event_id.slide_channel_id')
    slide_id = fields.Many2one('slide.slide', string='Course Content')
