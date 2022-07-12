import werkzeug

from odoo.api import Environment
import odoo.http as http

from odoo.http import request
from odoo import SUPERUSER_ID
from odoo import registry as registry_get
from odoo.tools.misc import get_lang
from odoo.addons.calendar.controllers.main import CalendarController


class CalendarController(CalendarController):

    @http.route('/calendar/meeting/view', type='http', auth="calendar")
    def view(self, db, token, action, id, view='calendar'):
        event_id = request.env['calendar.event'].sudo().search([('id', '=', int(id))], limit=1)
        if event_id.is_zoom_meeting:
            registry = registry_get(db)
            with registry.cursor() as cr:
                # Since we are in auth=none, create an env with SUPERUSER_ID
                env = Environment(cr, SUPERUSER_ID, {})
                attendee = env['calendar.attendee'].search([('access_token', '=', token), ('event_id', '=', int(id))])
                if not attendee:
                    return request.not_found()
                timezone = attendee.partner_id.tz
                lang = attendee.partner_id.lang or get_lang(request.env).code
                event = env['calendar.event'].with_context(tz=timezone, lang=lang).browse(int(id))

                if request.session.uid and request.env['res.users'].browse(request.session.uid).user_has_groups('base.group_user'):
                    return werkzeug.utils.redirect('/web?db=%s#id=%s&view_type=form&model=calendar.event' % (db, id))

                response_content = env['ir.ui.view'].with_context(lang=lang).render_template(
                    'to_zoom_calendar.invitation_page_anonymous', {
                        'event': event,
                        'attendee': attendee,
                        })
                return request.make_response(response_content, headers=[('Content-Type', 'text/html')])
        return super(CalendarController, self).view(db, token, action, id, view=view)
