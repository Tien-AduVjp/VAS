from odoo import fields, models, api, SUPERUSER_ID, _


class SocialNotice(models.Model):
    _name = 'social.notice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Notice from Users on the Page'
    _order = 'social_time desc'


    name = fields.Char(string='Name', compute='_compute_name')
    active = fields.Boolean(string='Active', default=True, tracking=True)
    post_id = fields.Many2one('social.post', 'Post')
    page_id = fields.Many2one('social.page', string='Page')
    type = fields.Selection([
            ('message', 'Message'),
            ('comment', 'Comment'),
            ('post', 'Post'),
            ('reaction', 'Reaction')
        ], string='Notice Type')
    is_seen = fields.Boolean(string='Seen?', default=False)
    social_post_id = fields.Char(string='Social Post ID')
    social_page_id = fields.Char(string='Social Page ID')
    social_user_id = fields.Char(string='Social User ID')
    social_user_name = fields.Char(string='Social User Name')
    social_comment_id = fields.Char(string='Social Comment Id')
    social_message = fields.Text(string='Social Message')
    social_time = fields.Datetime(string='Time on Social')
    social_participant_id = fields.Char(string='Social Participant Id', help='ID of participant in social conversation')
    post_link = fields.Char(string='Post Link', compute='_compute_post_link')
    photo = fields.Char(string='Photo Link')
    reaction_type = fields.Char(string='Reaction Type')

    @api.depends('page_id', 'post_id.name', 'social_user_name')
    def _compute_name(self):
        for r in self:
            name = 'Notification:'
            if r.type in ['reaction', 'comment']:
                name = _('Social notification: %s, %s') % (r.post_id.name, r.page_id.display_name)
            elif r.type == 'message':
                name = _('Social notification: %s - %s') % (r.social_user_name, r.page_id.display_name)
            r.name = name

    @api.depends('social_post_id')
    def _compute_post_link(self):
        for r in self:
            r.post_link = r._get_post_link()

    def _get_post_link(self):
        self.ensure_one()
        return False

    def toggle_active(self):
        return super(SocialNotice, self.sudo()).toggle_active()

    def action_view(self):
        self.ensure_one()
        self._is_seen()
        if self.type == 'comment' or self.type == 'reaction':
            action = self.env['ir.actions.act_window']._for_xml_id('viin_social.social_post_action')
            action['domain'] = "[('social_post_id', 'in', %s)]" % self.mapped('social_post_id')
            return action
        if self.type == 'message':
            action_id = self.env.ref('mail.action_discuss').id
            active_id = self.env['mail.channel'].search([('social_participant_id', '=', self.social_participant_id)]).id
            return {
                'type': 'ir.actions.act_url',
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
            partner_ids = r.page_id.member_ids.partner_id.ids or \
                        self.env.ref('viin_social.viin_social_group_admin').users.partner_id.ids
            if r.type == 'message':
                channel = channels.filtered(lambda c:c.social_participant_id == r.social_participant_id)[:1]
                channel.channel_last_seen_partner_ids.write({'is_pinned': True})

                body = self._get_body_message_notification({
                    'social_user_name': r.social_user_name,
                    'page_name': r.page_id.name,
                    'social_message': r.social_message
                })
                r.with_user(SUPERUSER_ID).message_post(body=body, partner_ids=partner_ids)
            elif r.type == 'comment' and self.env.company.receive_comment_notification:
                body = self._get_body_comment_notification({
                    'social_user_name': r.social_user_name,
                    'post_link': r.post_link,
                    'post_name': r.post_id.name,
                    'social_message': r.social_message,
                    'photo': r.photo
                })
                r.with_user(SUPERUSER_ID).message_post(body=body, partner_ids=partner_ids)
            elif r.type == 'reaction' and self.env.company.receive_reactive_notification:
                body = self._get_body_reaction_notification({
                    'social_user_name': r.social_user_name,
                    'post_link': r.post_link,
                    'post_name': r.post_id.name,
                    'reaction_type': r.reaction_type
                })
                r.with_user(SUPERUSER_ID).message_post(body=body, partner_ids=partner_ids)

    def _get_body_message_notification(self, datas):
        body = _("""
            <b>{social_user_name}</b> sent a message to {page_name} page: <br>
            {social_message}
        """)
        body = body.format(
            social_user_name=datas['social_user_name'],
            page_name=datas['page_name'],
            social_message=datas['social_message'] or False
        )
        return body

    def _get_body_comment_notification(self, datas):
        body = _("""
            <b>{social_user_name}</b> commented on the post <a href="{post_link}" target="_blank">{post_name}</a>: <br>
            {social_message} <br>
            {element_photo}
        """)
        if not datas.get('post_link', False):
            body = body.replace('<a href="{post_link}" target="_blank">{post_name}</a>', '<b>{post_name}</b>')

        body = body.format(
            social_user_name=datas['social_user_name'],
            post_link=datas.get('post_link', False) or '#',
            post_name=datas['post_name'] or _('a post on social media'),
            social_message=datas['social_message'] or '',
            element_photo='<img src="%s" style="max-height: 300px" />' % datas['photo'] if datas['photo'] else ''
        )
        return body

    def _get_body_reaction_notification(self, datas):
        body = _("""
            <b>{social_user_name}</b> reacted to the post <a href="{post_link}" target="_blank">{post_name}</a>: <br>
            {reaction_type}
        """)
        if not datas.get('post_link', False):
            body = body.replace('<a href="{post_link}" target="_blank">{post_name}</a>', '<b>{post_name}</b>')

        body = body.format(
            social_user_name=datas['social_user_name'],
            post_link=datas.get('post_link', ''),
            post_name=datas['post_name'],
            reaction_type=datas['reaction_type']
        )
        return body

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
