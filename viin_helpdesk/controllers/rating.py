from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request


class RatingTeam(http.Controller):

    @http.route(['/ticket/rating'], type='http', auth="public", website=True, sitemap=False)
    def index_ticket(self, **kw):
        tickets = request.env['helpdesk.ticket'].sudo().search([('rating_status', '!=', 'no'), ('portal_show_rating', '=', True)])
        values = {'tickets': tickets}
        return request.render('viin_helpdesk.rating_index', values)

    def _calculate_period_partner_stats(self, ticket_id=0, team_id=0):
        # get raw data: number of rating by rated partner, by rating value, by period
        query = """
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
                %s
                    AND res_model = 'helpdesk.ticket'
                    AND rated_partner_id IS NOT NULL
                    AND write_date >= current_date - interval '90' day
                    AND rating IN (1,5,10)
            GROUP BY
                rated_partner_id, rating, period
        """
        if team_id > 0:
            where_team = """
            parent_res_model = 'helpdesk.team'
                AND parent_res_id = %s
            """
            query = query % where_team
        elif ticket_id > 0:
            where_ticket = """
            res_id = %s
            """
            query = query % where_ticket
        else:
            return {
                'partner_statistics': {},
                'period_statistics': {},
            }
        request.env.cr.execute(query, (team_id,) if team_id > 0 else (ticket_id,))
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

    def _get_record_by_id(self, model, id):
        user = request.env.user
        Record = request.env[model]
        try:
            Record = Record.sudo().browse(int(id))
            if not Record.exists():
                return request.render("website.page_404")
        except ValueError:
            return request.render("website.page_404")
        if not ((Record.rating_status != 'no') and Record.portal_show_rating) and not user.has_group('viin_helpdesk.group_helpdesk_manager'):
            raise NotFound()
        return Record

    @http.route(['/ticket/rating/<ticket_id>'], type='http', auth="public", website=True, sitemap=False)
    def ticket_page(self, ticket_id=None, **kw):
        ticket = self._get_record_by_id('helpdesk.ticket', id=ticket_id)
        return request.render('viin_helpdesk.rating_helpdesk_ticket_rating_page', {
            'ticket': ticket,
            'ratings': request.env['rating.rating'].sudo().search([('consumed', '=', True), ('res_model', '=', 'helpdesk.ticket'), ('res_id', '=', ticket_id)], order='write_date DESC', limit=50),
            'statistics': self._calculate_period_partner_stats(ticket_id=int(ticket_id)),
        })

    @http.route(['/team/rating/<team_id>'], type='http', auth="public", website=True, sitemap=False)
    def team_page(self, team_id=None, **kw):
        team = self._get_record_by_id('helpdesk.team', id=team_id)
        return request.render('viin_helpdesk.rating_helpdesk_team_rating_page', {
            'team': team,
            'ratings': request.env['rating.rating'].sudo().search([('consumed', '=', True), ('parent_res_model', '=', 'helpdesk.team'), ('parent_res_id', '=', team_id)], order='write_date DESC', limit=50),
            'statistics': self._calculate_period_partner_stats(team_id=int(team_id)),
        })

