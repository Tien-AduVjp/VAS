# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied


class BlogPost(models.Model):
    _inherit = 'blog.post'

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        if not self.env.user.has_group('website.group_website_designer') and self.create_uid != self.env.user:
            raise AccessDenied(_("You are not allowed to perform this action."))
        return super(BlogPost, self).message_subscribe(partner_ids, channel_ids, subtype_ids)

    @api.depends('create_date', 'published_date')
    def _compute_post_date(self):
        if self.env.user.has_group('website.group_website_designer'):
            return super(BlogPost, self)._compute_post_date()
        for r in self:
            r.post_date = r.published_date or fields.Datetime.now()
