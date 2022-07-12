# -*- coding: utf-8 -*-
from odoo import models


class Page(models.Model):
    _inherit = 'website.page'

    def _compute_can_publish(self):
        super(Page, self)._compute_can_publish()
        if not self.env.user.has_group("website.group_website_designer"):
            for record in self:
                record.can_publish = False
