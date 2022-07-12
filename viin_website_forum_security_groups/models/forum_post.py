from odoo import api, models
from ..tools import bypass_karma_check_and_execute


class ForumPost(models.Model):
    _inherit = 'forum.post'

    def _get_post_karma_rights(self):
        super(ForumPost, self)._get_post_karma_rights()
        for r in self:
            if r.forum_id.is_moderator:
                r.karma_accept = 0
                r.karma_edit = 0
                r.karma_close = 0
                r.karma_unlink = 0
                r.karma_comment = 0
                r.karma_comment_convert = 0

                r.can_ask = True
                r.can_answer = True
                r.can_accept = True
                r.can_edit = True
                r.can_close = True
                r.can_unlink = True
                r.can_upvote = True
                r.can_downvote = True
                r.can_comment = True
                r.can_comment_convert = True
                r.can_view = True
                r.can_display_biography = True
                r.can_post = True
                r.can_flag = True
                r.can_moderate = True

    def write(self, vals):
        user = self.env.user
        if 'tag_ids' in vals:
            posts = self.filtered(lambda p: p.forum_id.is_moderator)
            if posts:
                max_karma_edit_retag = max(posts.forum_id.mapped('karma_edit_retag'))
                if user.karma < max_karma_edit_retag:
                    method = super(ForumPost, self).write
                    return bypass_karma_check_and_execute(user, max_karma_edit_retag, method, [vals])
        return super(ForumPost, self).write(vals)

    @api.model
    def convert_comment_to_answer(self, message_id, default=None):
        user = self.env.user
        comment = self.env['mail.message'].sudo().browse(message_id)
        post = self.browse(comment.res_id)
        if post.forum_id.is_moderator:
            is_author = comment.author_id.id == user.partner_id.id
            karma_convert = is_author and post.forum_id.karma_comment_convert_own or post.forum_id.karma_comment_convert_all
            if user.karma < karma_convert:
                method = super(ForumPost, self).convert_comment_to_answer
                return bypass_karma_check_and_execute(user, karma_convert, method, [message_id, default])
        return super(ForumPost, self).convert_comment_to_answer(message_id, default)

    def unlink_comment(self, message_id):
        user = self.env.user
        comment = self.env['mail.message'].sudo().browse(message_id)
        is_author = comment.author_id.id == user.partner_id.id
        if comment.model == 'forum.post':
            post = self.filtered(lambda p: p.id == comment.res_id)
            if post and post.forum_id.is_moderator:
                karma_unlink = is_author and post.forum_id.karma_comment_unlink_own or post.forum_id.karma_comment_unlink_all
                if user.karma < karma_unlink:
                    method = super(ForumPost, self).unlink_comment
                    return bypass_karma_check_and_execute(user, karma_unlink, method, [message_id])
        return super(ForumPost, self).unlink_comment(message_id)

    def _update_content(self, content, forum_id):
        user = self.env.user
        forum = self.env['forum.forum'].browse(forum_id)
        if user.karma < forum.karma_editor and forum.is_moderator:
            method = super(ForumPost, self)._update_content
            # Add an extra required karma because in the original method,
            # user can only post it if that user's karma is greater than the required
            return bypass_karma_check_and_execute(user, forum.karma_editor + 1, method, [content, forum_id])
        return super(ForumPost, self)._update_content(content, forum_id)
