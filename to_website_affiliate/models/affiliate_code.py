from odoo import fields, models, api, _


class AffiliateCode(models.Model):
    _name = 'affiliate.code'
    _inherit = ['affiliate.code', 'website.multi.mixin']

    website_description = fields.Html(string="Website Description", compute='_compute_website_description')

    # override
    website_id = fields.Many2one(help='The website to which the affiliate code is applied')

    @api.depends('name', 'website_id', 'website_id.domain', 'website_id.aff_url_param')
    def _compute_website_description(self):
        for r in self:
            if r.name and r.website_id and r.website_id.domain:
                r.website_description = _("""
                    In order to get started with the code <code>%s</code>,
                    just copy the URL <code>%s/?%s=%s</code> and share it with your friends and partners.
                    You can put the URL on your social network like Facebook, LinkedIn
                    or put it on webpages where you can to get more and more customers.
                    """) % (r.name, r.website_id.domain, r.website_id.aff_url_param, r.name)
            else:
                r.website_description = ""

    def _find_current_salesperson(self):
        self.ensure_one()
        return self.website_id.salesperson_id or super(AffiliateCode, self)._find_current_salesperson()

