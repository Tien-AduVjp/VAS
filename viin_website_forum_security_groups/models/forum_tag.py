from odoo import api, models
from ..tools import bypass_karma_check_and_execute


class ForumTag(models.Model):
    _inherit = 'forum.tag'

    @api.model
    def create(self, vals):
        user = self.env.user
        forum = self.env['forum.forum'].browse(vals.get('forum_id'))
        this = self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)
        if user.karma < forum.karma_tag_create and forum.is_moderator:
            method = super(ForumTag, this).create
            return bypass_karma_check_and_execute(user, forum.karma_tag_create, method, [vals])
        return super(ForumTag, this).create(vals)
