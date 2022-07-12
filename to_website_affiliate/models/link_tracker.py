from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.osv import expression


class LinkTracker(models.Model):
    _inherit = "link.tracker"

    affiliate_code_id = fields.Many2one('affiliate.code', string='Affiliate Code')

    @api.constrains('url', 'campaign_id', 'medium_id', 'source_id', 'affiliate_code_id')
    def _check_unicity(self):
        """Check that the link trackers are unique."""
        # build a query to fetch all needed link trackers at once
        search_query = expression.OR([
            expression.AND([
                [('url', '=', r.url)],
                [('campaign_id', '=', r.campaign_id.id)],
                [('medium_id', '=', r.medium_id.id)],
                [('source_id', '=', r.source_id.id)],
            ])
            for r in self
        ])

        # Can not be implemented with a SQL constraint because we want to care about null values.
        all_link_trackers = self.search(search_query)

        # check for unicity
        for r in self:
            if all_link_trackers.filtered(
                lambda l: l.url == r.url
                and l.campaign_id == r.campaign_id
                and l.medium_id == r.medium_id
                and l.source_id == r.source_id
                and l.affiliate_code_id == r.affiliate_code_id
            ) != r:
                if r.affiliate_code_id:
                    raise UserError(_(
                    'Link Tracker values (URL, campaign, medium, source and affiliate code) must be unique (%s, %s, %s, %s, %s).',
                    r.url,
                    r.campaign_id.name,
                    r.medium_id.name,
                    r.source_id.name,
                    r.affiliate_code_id.name,
                ))
                raise UserError(_(
                    'Link Tracker values (URL, campaign, medium and source) must be unique (%s, %s, %s, %s).',
                    r.url,
                    r.campaign_id.name,
                    r.medium_id.name,
                    r.source_id.name,
                ))

    @api.model
    def create(self, vals):
        # Origin: Do not create a new link tracker if it is the same (URL, campaign, medium and source)
        # Override: Do not create a new link tracker if it is the same (URL, campaign, medium, source and affiliate code)
        if 'affiliate_code_id' in vals:
            self = self.with_context(affiliate_code_id=vals['affiliate_code_id'])
        return super(LinkTracker, self).create(vals)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'affiliate_code_id' in self._context:
            args = expression.AND([[('affiliate_code_id', '=', self._context['affiliate_code_id'])], args])
        return super(LinkTracker, self).search(args, offset=offset, limit=limit, order=order, count=count)
