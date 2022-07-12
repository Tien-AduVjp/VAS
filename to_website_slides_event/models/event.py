from odoo import api, fields, models

class EventEvent(models.Model):
    _inherit = "event.event"
    
    slide_channel_id = fields.Many2one('slide.channel', string="Course")
    slide_ids = fields.Many2many('slide.slide', string='Course Contents', compute='_compute_slide_ids', store=True)
    
    @api.depends('track_ids.slide_id')
    def _compute_slide_ids(self):
        for r in self:
            r.slide_ids = r.track_ids.mapped('slide_id')
