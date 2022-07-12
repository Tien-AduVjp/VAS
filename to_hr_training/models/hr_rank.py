from odoo import models, fields, api


class HrRank(models.Model):
    _inherit = 'hr.rank'

    slide_channel_for_current_rank_ids = fields.Many2many('slide.channel', 'slide_channel_current_rank_rel',
                                                          compute='_compute_slide_channel_for_current_rank_ids',
                                                          store=True,
                                                          string='Courses for current rank')
    slide_channel_for_current_rank_count = fields.Integer(string='Number of courses for current rank',
                                                          compute='_compute_slide_channel_for_current_rank_count',
                                                          help="Number of courses required for current rank")
    slide_channel_for_next_targeted_rank_ids = fields.Many2many('slide.channel', 'slide_channel_next_targeted_rank_rel',
                                                       compute="_compute_slide_channel_for_next_targeted_rank_ids",
                                                       store=True,
                                                       string="Courses for next targeted rank")
    slide_channel_for_next_targeted_rank_count = fields.Integer(string='Courses for next rank',
                                                                compute='_compute_slide_channel_for_next_targeted_rank_count',
                                                                help="Number of courses required for next rank")

    @api.depends('consolidated_rank_skill_description_ids.skill_description_id.slide_channel_ids',
                 'job_line_ids.job_id.slide_channel_ids')
    def _compute_slide_channel_for_current_rank_ids(self):
        for r in self:
            r.slide_channel_for_current_rank_ids =\
                r.consolidated_rank_skill_description_ids.skill_description_id.slide_channel_ids\
                | r.job_line_ids.job_id.slide_channel_ids

    @api.depends('parent_id.consolidated_rank_skill_description_ids.skill_description_id.slide_channel_ids',
                 'parent_id.job_line_ids.job_id.slide_channel_ids',
                 'slide_channel_for_current_rank_ids')
    def _compute_slide_channel_for_next_targeted_rank_ids(self):
        for r in self:
            r.slide_channel_for_next_targeted_rank_ids =\
                (r.parent_id.consolidated_rank_skill_description_ids.skill_description_id.slide_channel_ids\
                | r.parent_id.job_line_ids.job_id.slide_channel_ids)\
                - r.slide_channel_for_current_rank_ids

    @api.depends('slide_channel_for_current_rank_ids')
    def _compute_slide_channel_for_current_rank_count(self):
        for r in self:
            r.slide_channel_for_current_rank_count = len(r.slide_channel_for_current_rank_ids)

    @api.depends('slide_channel_for_next_targeted_rank_ids')
    def _compute_slide_channel_for_next_targeted_rank_count(self):
        for r in self:
            r.slide_channel_for_next_targeted_rank_count = len(r.slide_channel_for_next_targeted_rank_ids)

    def action_view_slide_channel_current_rank(self):
        action = self.env['ir.actions.act_window']._for_xml_id('website_slides.slide_channel_action_overview')
        action['domain'] = "[('id','in',%s)]" % self.slide_channel_for_current_rank_ids.ids
        return action

    def action_view_slide_channel_next_rank(self):
        action = self.env['ir.actions.act_window']._for_xml_id('website_slides.slide_channel_action_overview')
        action['domain'] = "[('id','in',%s)]" % self.slide_channel_for_next_targeted_rank_ids.ids
        return action
