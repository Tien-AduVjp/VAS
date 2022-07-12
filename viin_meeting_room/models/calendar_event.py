import datetime

from odoo import models, fields , _, api
from odoo.exceptions import  UserError
from odoo.tools.date_utils import start_of


class Meeting(models.Model):
    _inherit = 'calendar.event'
    
    room_id = fields.Many2one('calendar.meeting.room', string='Meeting Room', tracking=True, copy=False)

    @api.constrains('recurrency', 'count', 'rrule_type', 'end_type', 'allday', 'room_id', 'start', 'stop', 'interval',
                    'mo', 'tu', 'we', 'th', 'fr', 'sa', 'su', 'month_by', 'day', 'week_list', 'byday', 'final_date')
    def _check_duplicate_room_time(self):
        """Check the meeting room overlap """
        if not self:
            return

        min_start_date = sorted(self.mapped('start'))[0]
        max_stop_date = sorted(self.mapped(lambda e: e._get_recurrency_end_date() and datetime.datetime.combine(e._get_recurrency_end_date(), datetime.time.max) or () or e.stop), reverse=True)[0]
        domain_event = [('start', '<', max_stop_date + datetime.timedelta(days=1)),
                        ('room_id', 'in', self.room_id.ids),
                        '|', ('stop', '>', min_start_date - datetime.timedelta(days=1)),
                        '&', ('recurrency', '=', True), ('final_date', '>=', min_start_date.date())]
        event_ids = self.with_context(virtual_id=False).search(domain_event).get_recurrent_ids([])
        events = self.browse(event_ids)
        to_check_ids = self.filtered(lambda e: e.room_id).get_recurrent_ids([])
        to_date = fields.Date.to_date
        to_datetime = fields.Datetime.to_datetime
        to_time_tz = self.env['to.base'].convert_utc_time_to_tz
        datetime_check = start_of(fields.Datetime.now(), 'day')
        for r in self.browse(to_check_ids).filtered(lambda e: to_datetime(e.start) >= datetime_check or to_datetime(e.stop) >= datetime_check):
            for event in events.filtered(lambda e: e.room_id == r.room_id) - r:
                # if r as allday meeting or event as allday meeting
                if r.allday or event.allday:
                    event_allday, event_rm = (r+event).sorted(lambda r: not r.allday)
                    
                    #Case event is recurrency type, need covert str type to datetime type
                    event_rm_stop = to_datetime(event_rm.stop) 
                    event_rm_start = to_datetime(event_rm.start)
                    tz = self._context.get('tz', False)
                    
                    if not event_rm.allday:
                        event_rm_stop = to_time_tz(event_rm_stop, tz)
                        event_rm_start = to_time_tz(event_rm_start, tz)
                    
                    if to_date(event_allday.start) > to_date(event_rm_stop) or to_date(event_allday.stop) < to_date(event_rm_start):
                        continue
                elif to_datetime(r.start) >= to_datetime(event.stop) or to_datetime(r.stop) <= to_datetime(event.start):
                    continue
                raise UserError(_("You may not be able to book the meeting room %(room)s while it is currently booked for the event %(event)s. \
You may shift your event to other time or contact %(owner)s who is the owner of the event %(event)s if you want to convince she or he to give you this slot.")
                % {'room':r.room_id.name, 'event':event.name, 'owner':event.user_id.name})

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.location = self.room_id.location
        else:
            self.location = self._origin.location
    
    def action_unarchive(self):
        res = super(Meeting, self).action_unarchive()
        self._check_duplicate_room_time()
        return res
