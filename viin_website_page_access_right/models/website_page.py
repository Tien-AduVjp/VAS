# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Page(models.Model):
    _inherit = 'website.page'

    def _compute_can_publish(self):
        super(Page, self)._compute_can_publish()
        if not self.env.user.has_group("website.group_website_designer"):
            group_website_publisher = self.env.context.get('group_website_publisher', False)
            for record in self:
                record.can_publish = group_website_publisher
               
    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group("website.group_website_designer"):
            self = self.with_context(group_website_publisher=True)
        return super(Page, self).create(vals_list)
