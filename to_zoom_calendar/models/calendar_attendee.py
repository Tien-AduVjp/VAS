from odoo import models, fields, api


class CalendarAttendee(models.Model):
    _inherit = 'calendar.attendee'

    @api.depends('zoom_meeting_attendee_url', 'event_id.user_id')
    def _get_zoom_meeting_start_url(self):
        for r in self:
            r.zoom_meeting_start_url = ''
            if r.partner_id.id == r.event_id.user_id.partner_id.id:
                r.zoom_meeting_start_url = r.event_id.zoom_meeting_start_url
                
    def _send_mail_to_attendees(self, template_xmlid, force_send=False, force_event_id=None):
        for r in self:
            if r.event_id.is_zoom_meeting:
                if template_xmlid == 'calendar.calendar_template_meeting_invitation':
                    template_xmlid = 'to_zoom_calendar.calendar_template_meeting_invitation'
                elif template_xmlid == 'calendar.calendar_template_meeting_changedate':
                    template_xmlid = 'to_zoom_calendar.calendar_template_meeting_changedate'
                elif template_xmlid == 'calendar.calendar_template_meeting_reminder':
                    template_xmlid = 'to_zoom_calendar.calendar_template_meeting_reminder'
        return super(CalendarAttendee, self)._send_mail_to_attendees(template_xmlid, force_send=force_send, force_event_id=force_event_id)
