from odoo import api, fields, models


class HrSkillDescription(models.Model):
    _inherit = 'hr.skill.description'

    slide_channel_ids = fields.Many2many('slide.channel',
                                        string='Courses',
                                        help="Course's list related to this skill level")
    slide_channel_count = fields.Integer(string='Courses Count',
                                         compute='_compute_slide_channel_count',
                                         help="Number of courses required for this this skill level")

    @api.depends('slide_channel_ids')
    def _compute_slide_channel_count(self):
        for r in self:
            r.slide_channel_count = len(r.slide_channel_ids)

    def action_view_slide_channel(self):
        action = self.env['ir.actions.act_window']._for_xml_id('website_slides.slide_channel_action_overview')
        action['domain'] = "[('id','in',%s)]" % self.slide_channel_ids.ids
        return action
