from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request


class RatingPortal(http.Controller):

    def _calculate_period_partner_stats(self, project_id):
        # get raw data: number of rating by rated partner, by rating value, by period
        request.env.cr.execute("""
            SELECT
                rated_partner_id,
                rating,
                COUNT(rating) as rating_count,
                CASE
                    WHEN now()::date - write_date::date BETWEEN 0 AND 6 Then 'days_06'
                    WHEN now()::date - write_date::date BETWEEN 0 AND 15 Then 'days_15'
                    WHEN now()::date - write_date::date BETWEEN 0 AND 30  Then 'days_30'
                    WHEN now()::date - write_date::date BETWEEN 0 AND 90  Then 'days_90'
                END AS period
            FROM
                rating_rating
            WHERE
                res_id = %s
                AND res_model = 'sale.subscription'
                AND rated_partner_id IS NOT NULL
                AND write_date >= current_date - interval '90' day
                AND rating IN (1,5,10)
            GROUP BY
                rated_partner_id, rating, period
        """, (project_id, ))

        raw_data = request.env.cr.dictfetchall()

        # periodical statistics
        default_period_dict = {'rating_10': 0, 'rating_5': 0, 'rating_1': 0, 'total': 0}
        period_statistics = {
            'days_06': dict(default_period_dict),
            'days_15': dict(default_period_dict),
            'days_30': dict(default_period_dict),
            'days_90': dict(default_period_dict),
        }
        for period_statistics_key in period_statistics.keys():
            for row in raw_data:
                if row['period'] <= period_statistics_key:
                    period_statistics[period_statistics_key]['rating_%s' % (int(row['rating']),)] += row['rating_count']
                    period_statistics[period_statistics_key]['total'] += row['rating_count']

        # partner statistics
        default_partner_dict = {'rating_10': 0, 'rating_5': 0, 'rating_1': 0, 'total': 0, 'rated_partner': None, 'percentage_happy': 0.0}
        partner_statistics = {}
        for row in raw_data:
            if row['period'] <= 'days_15':
                if row['rated_partner_id'] not in partner_statistics:
                    partner_statistics[row['rated_partner_id']] = dict(default_partner_dict)
                    partner_statistics[row['rated_partner_id']]['rated_partner'] = request.env['res.partner'].sudo().browse(row['rated_partner_id'])
                partner_statistics[row['rated_partner_id']]['rating_%s' % (int(row['rating']),)] += row['rating_count']
                partner_statistics[row['rated_partner_id']]['total'] += row['rating_count']

        for partner_id, stat_values in partner_statistics.items():
            stat_values['percentage_happy'] = (stat_values['rating_10'] / float(stat_values['total'])) * 100 if stat_values['total'] else 0.0

        return {
            'partner_statistics': partner_statistics,
            'period_statistics': period_statistics,
        }

    @http.route(['/subscription/rating/<int:subscription_id>'], type='http', auth="public", website=True)
    def page(self, subscription_id=None, **kw):
        subscription = request.env['sale.subscription'].sudo().browse(subscription_id)
        # to avoid giving any access rights on subscriptions to the public user, let's use sudo
        # and check if the user should be able to view the subscription (subscription managers only if it's unpublished or has no rating)
        if not ((subscription.rating_status != 'no') and subscription.portal_show_rating) and not request.env.user.has_group('to_sale_subscription.group_sale_subscription_manager'):
            raise NotFound()

        return request.render('to_sale_subscription.rating_subscription_rating_page', {
            'subscription': subscription,
            'ratings': request.env['rating.rating'].sudo().search([('consumed', '=', True), ('res_model', '=', 'sale.subscription'), ('res_id', '=', subscription_id)], order='write_date DESC', limit=50),
            'statistics': self._calculate_period_partner_stats(subscription_id),
        })
