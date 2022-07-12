import base64
import json
from collections import OrderedDict
from operator import itemgetter

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


def _insert_attachments(env, ticket, **post):
    attachments = []
    for field_name, field_value in post.items():
        # If the value of the field if a file
        if hasattr(field_value, 'filename'):
            # Undo file upload field name indexing
            field_name = field_name.split('[', 1)[0]
            field_value.field_name = field_name
            attachments.append({
                'name': field_value.filename,
                'datas': base64.encodebytes(field_value.read()),
                'res_model': ticket._name,
                'res_id': ticket.id,
                })
    
    if attachments:
        attachment_ids = env['ir.attachment'].sudo().create(attachments)
        ticket.write({'attachment_ids': [(6, 0, attachment_ids.ids)]})

def _prepare_ticket_vals(env, **post):
    vals = {
        'name': post.get('name', ''),
        'description': post.get('description', ''),
        'team_id': int(post.get('team_id', env.company.default_helpdesk_team_id.id)),
        'send_notification_email': True,
        }
    
    if env.user != env.ref('base.public_user', raise_if_not_found=False):
        vals.update({
            'partner_id': env.user.partner_id.id,
            })
    return vals

class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super(CustomerPortal, self)._prepare_home_portal_values()
        values['tickets_count'] = request.env['helpdesk.ticket'].search_count(self._prepare_ticket_domain())
        return values

    def _prepare_ticket_domain(self):
        # new user = portal
        user = request.env.user
        if user.has_group('viin_helpdesk.group_helpdesk_manager'):
            return []
        return ['|','|','|',
                    ('user_id', '=', user.id),
                    ('create_uid', '=', user.id),
                    ('partner_id', '=', user.partner_id.id),
                    ('message_partner_ids', 'child_of', [user.partner_id.commercial_partner_id.id])]

    def _get_create_ticket_url(self, **kw):
        return '/my/tickets/create'

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tickets(self, page=1, sortby=None, filterby=None, search=None, search_in='content', groupby='team', **kw):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        Tickets = request.env['helpdesk.ticket']
        # TODO: Filter by User
        domain = self._prepare_ticket_domain()

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Title'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'partner': {'label': _('Partner'), 'order': 'partner_id'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'team': {'input': 'team', 'label': _('Team')},
            'partner': {'input': 'partner', 'label': _('Partner')},
            'stage': {'input': 'stage', 'label': _('Stage')},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> in (Title or Name)</span>')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'stage': {'input': 'stage', 'label': _('Search in Stages')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('stage', 'all'):
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain += search_domain

        tickets_count = Tickets.search_count(domain)
        pager = portal_pager(
            url="/my/tickets/",
            url_args={'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        if groupby == 'team':
            order = "team_id, %s" % order  # force sort on team first to group by team in view
        elif groupby == 'partner':
            order = "partner_id, %s" % order
        elif groupby == 'stage':
            order = "stage_id, %s" % order
        
        tickets = Tickets.search(domain, order=order, limit=self._items_per_page, offset=(page - 1) * self._items_per_page)
        request.session['my_tickets_history'] = tickets.ids[:100]
        if groupby == 'team':
            grouped_tickets = [request.env['helpdesk.ticket'].concat(*g) for k, g in groupbyelem(tickets, itemgetter('team_id'))]
        elif groupby == 'partner':
            grouped_tickets = [request.env['helpdesk.ticket'].concat(*g) for k, g in groupbyelem(tickets, itemgetter('partner_id'))]
        elif groupby == 'stage':
            grouped_tickets = [request.env['helpdesk.ticket'].concat(*g) for k, g in groupbyelem(tickets, itemgetter('stage_id'))]
        else:
            grouped_tickets = [tickets]

        values.update({
            'tickets': tickets,
            'page_name': 'tickets',
            'default_url': '/my/tickets/',
            'create_ticket_url': self._get_create_ticket_url(**kw),
            'pager': pager,
            'grouped_tickets': grouped_tickets,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'search_in': search_in,
            'filterby': filterby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })

        return request.render('viin_helpdesk.portal_my_tickets', values)

    def _ticket_get_page_view_values(self, ticket, access_token, **kwargs):
        values = {
            'page_name': 'tickets',
            'ticket': ticket,
            'user': request.env.user,
        }
        return self._get_page_view_values(ticket, access_token, values, 'my_tickets_history', False, **kwargs)

    @http.route(['/my/tickets/<int:ticket_id>'], type='http', auth="public", website=True, csrf=True)
    def portal_my_ticket(self, ticket_id, access_token=None, **kw):
        try:
            ticket_sudo = self._document_check_access('helpdesk.ticket', ticket_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._ticket_get_page_view_values(ticket_sudo, access_token, **kw)
        return request.render("viin_helpdesk.portal_my_ticket", values)

    @http.route('/my/tickets/create', type='http', auth='user', methods=['GET', 'POST'], website=True, csrf=True)
    def _create_new_helpdesk(self, **post):
        if request.httprequest.method == 'GET':
            values = self._prepare_portal_layout_values()
            values.update({
                'teams': request.env['helpdesk.team'].sudo().search([('company_id', '=', request.env.company.id), ('privacy_visibility', '=', 'portal')])
                })
            return request.render('viin_helpdesk.create_ticket_from_portal', values)
        
        vals = _prepare_ticket_vals(request.env, **post)
        ticket = request.env['helpdesk.ticket'].sudo().create(vals)
        ticket.flush()
        _insert_attachments(request.env, ticket, **post)
        return json.dumps({'id': ticket.id})
