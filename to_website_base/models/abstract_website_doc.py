# -*- coding: utf-8 -*-
from odoo import fields, models, api
from psycopg2.extensions import AsIs
from odoo.http import request


class AbstractWebsiteDoc(models.AbstractModel):
    _name = 'abstract.website.doc'
    _inherit = 'website.multi.mixin'
    _description = "Abstract Website Document"

    @api.model
    def _get_default_website(self):
        website = False
        try:
            website = request.website
        except:
            pass
        if not website:
            website = self.env['website'].get_current_website()
            try:
                request.website = website
            except:
                pass
        return website

    @api.model
    def _get_default_author(self):
        if self.env.user:
            return self.env.user.partner_id
        return False

    website_id = fields.Many2one(default=_get_default_website)
    author_id = fields.Many2one('res.partner', string='Author', index=True, default=_get_default_author,
                                help="The partner who is the author of this document")
    views = fields.Integer('Views', default=0, required=True, help="Number of views from websites")
    
    def increase_views(self):
        self.env.cr.execute("UPDATE %s SET views = views + 1 WHERE id IN %s;", (AsIs(self._table), tuple(self.ids)))
        
    def _compute_can_publish(self):
        for r in self:
            r.can_publish = True

