from odoo.http import request

from odoo.addons.viin_helpdesk.controllers import portal
from odoo.addons.viin_helpdesk.controllers.portal import CustomerPortal

_prepare_ticket_vals = portal._prepare_ticket_vals
def _prepare_ticket_vals_plus(env, **post):
        """ Update sale_order_id and team_id to Create Ticket from that SO
        """
        vals = _prepare_ticket_vals(env, **post)
        saleorder = post.get('saleorder', False)
        if saleorder:
            vals.update({
                'sale_order_id': int(saleorder),
                'team_id': env['helpdesk.team'].sudo().with_context(lang='en_US').search([('name', '=', 'Customer Support')], limit=1).id \
                           or env.company.default_helpdesk_team_id.id
                 })
        return vals

portal._prepare_ticket_vals = _prepare_ticket_vals_plus

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        saleorder = request.params.get('saleorder', False)
        if saleorder:
            values.update({'saleorder': saleorder})
        return values

    def _prepare_ticket_domain(self):
        vals = super(CustomerPortal, self)._prepare_ticket_domain()
        saleorder = request.params.get('saleorder', False)
        if saleorder:
            vals += [('sale_order_id', '=', int(saleorder))]
        return vals

    def _get_create_ticket_url(self, **kw):
        url = super(CustomerPortal, self)._get_create_ticket_url(**kw)
        saleorder = kw.get('saleorder', False)
        if saleorder:
            url += '?saleorder=%s' %int(saleorder)
        return url
