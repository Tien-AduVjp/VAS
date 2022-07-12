from odoo import fields, models


class AffiliateReferrerAnalysis(models.Model):
    _inherit = 'report.affiliate.referrer.analysis'

    number_so = fields.Integer(string="# Sales Orders", readonly=True)
    amount_so = fields.Float(string="Amount", readonly=True, digits='Account')

    def _select(self):
        sql = super(AffiliateReferrerAnalysis, self)._select()
        sql += ''',
            (SELECT count(*) FROM sale_order so WHERE so.referrer_analysis_id = a.id AND so.state NOT IN ('draft', 'cancel', 'sent')) AS number_so,
            (SELECT sum(amount_total) FROM sale_order so WHERE so.referrer_analysis_id = a.id AND so.state NOT IN ('draft', 'cancel', 'sent')) AS amount_so
        '''
        return sql

    def _group_by(self):
        sql = super(AffiliateReferrerAnalysis, self)._group_by()
        sql += ''',
            number_so,
            amount_so
        '''
        return sql

