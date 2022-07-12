from odoo import models, fields


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    slide_channel_for_current_rank_ids = fields.Many2many(related='rank_id.slide_channel_for_current_rank_ids',
                                                          string='Courses for current rank')
    slide_channel_for_next_targeted_rank_ids = fields.Many2many(related='rank_id.slide_channel_for_next_targeted_rank_ids',
                                                                string="Courses for next targeted rank")
    slide_channel_for_current_rank_count = fields.Integer(string='Number of Courses for current rank',
                                                          related='rank_id.slide_channel_for_current_rank_count')
    slide_channel_for_next_targeted_rank_count = fields.Integer(string='Number of Courses for next rank',
                                                          related='rank_id.slide_channel_for_next_targeted_rank_count')

    def action_view_slide_channel_current_rank(self):
        action = self.env['ir.actions.act_window']._for_xml_id('website_slides.slide_channel_action_overview')
        action['domain'] = "[('id','in',%s)]" % self.slide_channel_for_current_rank_ids.ids
        return action

    def action_view_slide_channel_next_rank(self):
        action = self.env['ir.actions.act_window']._for_xml_id('website_slides.slide_channel_action_overview')
        action['domain'] = "[('id','in',%s)]" % self.slide_channel_for_next_targeted_rank_ids.ids
        return action
