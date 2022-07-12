from odoo import models, fields


class Website(models.Model):
    _inherit = 'website'

    noindex_nofollow = fields.Boolean(string="No Index, No Follow", help="No Index: Disallow the site to appear in search engines like Google, Bing, etc.\nNo Follow: None of the links on your pages will be followed", default=False)
