from odoo import fields, models


class SocialNotice(models.Model):
    _name = 'social.notice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Notice from Users on the Page'
    _order = 'social_time desc'
    _rec_name = 'page_id'
    
    post_id = fields.Many2one('social.post', 'Post')
    page_id = fields.Many2one('social.page', string='Page')
    type = fields.Selection([('message', 'Message'), ('comment', 'Comment'), ('post', 'Post')], string='Notice Type')
    is_seen = fields.Boolean(string='Seen?', default=False)
    social_post_id = fields.Char(string='Social Post ID')
    social_page_id = fields.Char(string='Social Page ID')
    social_user_id = fields.Char(string='Social User ID')
    social_user_name = fields.Char(string='Social User Name')
    social_comment_id = fields.Char(string='Social Comment Id')
    social_message = fields.Text(string='Social Message')
    social_time = fields.Datetime(string='Time on Social')
    social_participant_id = fields.Char(string='Social Participant Id', help='ID of participant in social conversation')
    
    def action_view(self):
        self.ensure_one()
        self._is_seen()
        if self.type == 'comment':
            action = self.env.ref('viin_social.social_post_action')
            result = action.read()[0]
            result['domain'] = "[('social_post_id', 'in', %s)]" % (self.mapped('social_post_id'))
            return result
        if self.type == 'message':
            action_id = self.env.ref('mail.action_discuss').id
            active_id = self.env['mail.channel'].search([('social_participant_id', '=', self.social_participant_id)]).id
            return { 'type': 'ir.actions.act_url',
                    'url': self.get_base_url() + '/web#action=%s&active_id=%s' % (action_id, active_id),
                    'target': 'self'
                }

    def action_read_all_notices(self):
        self.search([('is_seen', '=', False)])._is_seen()

    def _is_seen(self):
        self.sudo().write({'is_seen': True})

    def _create_notice(self, datas):
        val_lits = self._prepare_data(datas)
        if val_lits:
            notices = self.sudo().create(val_lits)
            notices.flush()
            notices._send_notification_to_users()
    
    def _send_notification_to_users(self):
        channels = self.env['mail.channel'].search([('social_participant_id', 'in', self.mapped('social_participant_id'))])
        for r in self:
            if r.type == 'message':
                # Message: send notifications to all members in channel
                channel = channels.filtered(lambda c:c.social_participant_id == r.social_participant_id)
                partner_ids = channel.channel_last_seen_partner_ids.partner_id.ids
                channel.message_post(body=r.social_message, partner_ids=partner_ids)
            else:
                # Comment: send notifications to all members on the page
                partner_ids = r.page_id.member_ids.partner_id.ids or r.page_id.media_id.assign_id.partner_id.ids
                if not partner_ids:
                    partner_ids = self.env['res.users'].search([('groups_id', 'in', self.env.ref('viin_social.viin_social_group_admin').ids)], limit=1).ids
                r.message_post(body=r.social_message, partner_ids=partner_ids)

    def _prepare_data(self, datas):
        for data in datas:
            # social_page_id, social_post_id
            social_post_id = data.get('social_post_id', False)
            if social_post_id:
                post_id = self.env['social.post'].search([('social_post_id', '=', social_post_id)], limit=1)
                if post_id:
                    page_id = post_id.page_id
                    data['post_id'] = post_id.id
                    if not page_id:
                        social_page_id = data.get('social_page_id', False)
                        if social_page_id:
                            page = self.env['social.page'].search([('social_page_id', '=', social_page_id)], limit=1)
                            data['page_id'] = page.id
                    else:
                        data['page_id'] = page_id.id
                else:
                    # If False then ignore (post is not synchronized or active=False
                    datas.remove(data)
        return datas
