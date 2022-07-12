from odoo import models


class HelpdeskTeam(models.Model):
    _name = 'helpdesk.team'
    _inherit = ['helpdesk.team', 'website.seo.metadata', 'website.published.multi.mixin']

    def _compute_website_url(self):
        for team in self:
            team.website_url = team.get_website_url()

    def get_website_url(self):
        self.ensure_one()
        return '/ticket/team/%d' % self.id

