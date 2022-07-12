from odoo import fields, api, models, _
from odoo.exceptions import UserError
from odoo.tools import html2plaintext, html_escape


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    active = fields.Boolean(string='Active', default=True)
    channel_type = fields.Selection(selection_add=[('social_chat', 'Social Conversation')])
    social_conversation_id = fields.Char(string='Social Conversation ID', help='ID of social conversation')
    social_page_id = fields.Many2one('social.page', string="Social Page ID")
    social_participant_id = fields.Char(string='Social Participant ID', help='ID of participant in social conversation')
    social_user_name = fields.Char(string='Social User Name')

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        self.ensure_one()
        if self.social_conversation_id and self.channel_type == 'social_chat':
            if kwargs['attachment_ids']:
                raise UserError(_("File attachments are not supported yet."))

            message = super(MailChannel, self).message_post(**kwargs)

            body = kwargs['body']
            social_page = self.social_page_id
            social_participant_id = self.social_participant_id

            custom_method = '_send_social_message_%s' % social_page.media_id.social_provider
            if hasattr(message, custom_method):
                getattr(message, custom_method)(body, social_page, social_participant_id)
            return message
        return super(MailChannel, self).message_post(**kwargs)

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
