from odoo import models, fields, api

class Message(models.Model):
    _inherit = 'mail.message'
    
    social_message_id = fields.Char(string='Social Message ID', help='ID of social message')
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super(Message, self).create(vals_list)
        social_conversations = self.env['mail.channel'].search([('channel_type', '=', 'social_chat')])
        social_messages = records.filtered_domain([('res_id', 'in', social_conversations.ids),('message_type','=','comment'),('model','=','mail.channel')])
        social_messages._send_social_message()
        return records
    
    def _send_social_message(self):
        social_conversations = self.env['mail.channel'].search([('id', 'in', self.mapped('res_id'))])
        for r in self:
            social_conversation = social_conversations.filtered_domain([('id', '=', r.res_id)])
            if social_conversation:
                social_page = social_conversation.social_page_id
                social_participant_id = social_conversation.social_participant_id
                if social_page and social_page.media_id.social_provider != 'none':
                    custom_send_social_message_method = '_send_social_message_%s' % social_page.media_id.social_provider
                    if hasattr(self, custom_send_social_message_method):
                        getattr(r, custom_send_social_message_method)(social_page, social_participant_id)
