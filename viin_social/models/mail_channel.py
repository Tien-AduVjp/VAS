from odoo import fields, api, models

class MailChannel(models.Model):
    _inherit = 'mail.channel'
    
    channel_type = fields.Selection(selection_add=[('social_chat', 'Social Conversation')])
    social_conversation_id = fields.Char(string='Social Conversation ID', help='ID of social conversation')
    social_page_id = fields.Many2one('social.page', string="Social Page ID")
    social_participant_id = fields.Char(string='Social Participant ID', help='ID of participant in social conversation')
    
    
    def _compute_is_chat(self):
        super(MailChannel, self)._compute_is_chat()
        for record in self:
            if record.channel_type == 'social_chat':
                record.is_chat = True

    def channel_info(self, extra_info=False):
        channel_infos = super(MailChannel, self).channel_info(extra_info)
        channel_infos_dict = dict((c['id'], c) for c in channel_infos)
        for r in self:
            if r.channel_type == 'social_chat':
                channel_infos_dict[r.id]['social_page_id'] = r.social_page_id.id
        return list(channel_infos_dict.values())

    @api.model
    def channel_fetch_slot(self):
        values = super(MailChannel, self).channel_fetch_slot()
        pinned_channels = self.env['mail.channel.partner'].search([('channel_id.channel_type', '=', 'social_chat'), ('partner_id', '=', self.env.user.partner_id.id), ('is_pinned', '=', True)]).channel_id
        values['channel_social_chat'] = pinned_channels.channel_info()
        return values
