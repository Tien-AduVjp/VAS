# -*- coding: utf-8 -*-
from collections import OrderedDict

from odoo import http
from odoo.http import request
from odoo.tools.translate import _

from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager, CustomerPortal


class CustomerPortal(CustomerPortal):

    def _prepare_subscription_domain(self, partner):
        return [
            ('partner_id.id', 'in', [partner.id, partner.commercial_partner_id.id]),
        ]

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        domain = self._prepare_subscription_domain(request.env.user.partner_id)
        values.update({
            'subscription_count': request.env['sale.subscription'].search_count(domain),
            })
        return values

    @http.route(['/my/subscriptions', '/my/subscriptions/page/<int:page>'], type='http', auth="user", website=True)
    def my_subscriptions(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        SaleSubscription = request.env['sale.subscription']

        domain = self._prepare_subscription_domain(request.env.user.partner_id)

        archive_groups = self._get_archive_groups('sale.subscription', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'open': {'label': _('In Progress'), 'domain': [('in_progress', '=', True)]},
            'pending': {'label': _('To Renew'), 'domain': [('to_renew', '=', True)]},
            'close': {'label': _('Closed'), 'domain': [('in_progress', '=', False)]},
        }

        # default sort by date
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by all
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        subscription_count = SaleSubscription.search_count(domain)
        pager = portal_pager(
            url="/my/subscriptions",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=subscription_count,
            page=page,
            step=self._items_per_page
        )

        subscriptions = SaleSubscription.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_subscriptions_history'] = subscriptions.ids[:100]

        values.update({
            'subscriptions': subscriptions,
            'page_name': 'subscriptions',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/subscriptions',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("to_sale_subscription.portal_my_subscriptions", values)
