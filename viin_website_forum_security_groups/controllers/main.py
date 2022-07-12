from odoo import http
from odoo.http import request
from odoo.addons.website_forum.controllers.main import WebsiteForum
from ..tools import bypass_karma_check_and_execute


class Forum(WebsiteForum):

    @http.route()
    def question(self, forum, question, **post):
        user = request.env.user
        if question.state == 'pending' and user.karma < forum.karma_post and question.create_uid != user:
            method = super(Forum, self).question
            return bypass_karma_check_and_execute(user, forum.karma_post, method, [forum, question], post)
        return super(Forum, self).question(forum, question, **post)

    @http.route()
    def validation_queue(self, forum, **kwargs):
        user = request.env.user
        if user.karma < forum.karma_moderate:
            method = super(Forum, self).validation_queue
            return bypass_karma_check_and_execute(user, forum.karma_moderate, method, [forum], kwargs)
        return super(Forum, self).validation_queue(forum, **kwargs)

    @http.route()
    def flagged_queue(self, forum, **kwargs):
        user = request.env.user
        if user.karma < forum.karma_moderate:
            method = super(Forum, self).flagged_queue
            return bypass_karma_check_and_execute(user, forum.karma_moderate, method, [forum], kwargs)
        return super(Forum, self).flagged_queue(forum, **kwargs)

    @http.route()
    def offensive_posts(self, forum, **kwargs):
        user = request.env.user
        if user.karma < forum.karma_moderate:
            method = super(Forum, self).offensive_posts
            return bypass_karma_check_and_execute(user, forum.karma_moderate, method, [forum], kwargs)
        return super(Forum, self).offensive_posts(forum, **kwargs)
