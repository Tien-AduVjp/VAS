import pytz
import datetime
from random import randint
from odoo import models, fields, api, registry, _
from odoo.exceptions import ValidationError, UserError


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    zoom_meeting_id = fields.Char(string='Zoom Meeting Id')
    zoom_user_id = fields.Many2one('zoom.user', string='Zoom Meeting Host', help='This is host ID for the meeting.')
    zoom_name = fields.Char(string='Zoom Meeting Subject')
    zoom_type = fields.Selection([
        ('1', 'Instant meeting'),
        ('2', 'Scheduled'),
        ('3', 'Recurring meeting with no fixed time'),
        ('8', 'Recurring meeting with fixed time')],
        string='Meeting Type',
        default='2', required=True)
    zoom_start_datetime = fields.Datetime(string='Starting at')
    zoom_duration = fields.Integer(string='Zoom Duration')
    zoom_description = fields.Text(string='Zoom Description')

    zoom_recurrency = fields.Boolean('Recurrences')
    zoom_interval = fields.Integer(string='Zoom Repeat Every')
    zoom_rrule_type = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly')], default='daily', string='Zoom Recurrence Type')
    zoom_end_type = fields.Selection([('count', 'Number of repetitions'),
                                      ('end_date', 'End date')], default='count', string='Until')
    zoom_count = fields.Integer(string='Zoom Repeat')
    zoom_final_date = fields.Date('Zoom Repeat Until')

    zoom_su = fields.Boolean('Sunday')
    zoom_mo = fields.Boolean('Monday')
    zoom_tu = fields.Boolean('Tuesday')
    zoom_we = fields.Boolean('Wednesday')
    zoom_th = fields.Boolean('Thursday')
    zoom_fr = fields.Boolean('Friday')
    zoom_sa = fields.Boolean('Saturday')

    zoom_meeting_attendee_url = fields.Char('Attendee URL', help='URL to join the meeting')
    zoom_meeting_start_url = fields.Char('Start URL', help='URL to start the meeting')
    is_zoom_meeting = fields.Boolean('Is Zoom Meeting?')

    zoom_setting = fields.Boolean('Settings')
    zoom_setting_join_before_host = fields.Boolean(string='Enable join before host', help='Allow participants to join the meeting before the host starts the meeting')
    zoom_setting_mute_upon_entry = fields.Boolean(string='Mute participants upon entry', help='Mute participants upon entry')
    zoom_setting_approval_type = fields.Selection([
        ('0', 'Automatically approve'),
        ('1', 'Manually approve'),
        ('2', 'No registration required')],
        string='Approval Type',
        default='2')
    zoom_setting_auto_recording = fields.Selection([
        ('local', 'Record on local'),
        ('cloud', 'Record on cloud'),
        ('none', 'Disabled')],
        string='Automatic Recording',
        default='local')
    is_owner_zoom = fields.Boolean(compute='_get_owner_zoom', help='A technical field to show/hide Zoom meeting information.')

    @api.constrains('zoom_user_id', 'zoom_duration', 'zoom_start_datetime')
    def _constrains_zoom_user_id(self):
        to_base = self.env['to.base']
        for r in self:
            if r.is_zoom_meeting and not r._check_zoom_user_id(r.zoom_user_id.zoom_email):
                zoom_start_datetime = to_base.convert_utc_time_to_tz(r.zoom_start_datetime)
                raise UserError(_('Zoom: Host that you selected that have been used at %s. Please wait for the Administration to add the Host.') % zoom_start_datetime)

    @api.onchange('zoom_start_datetime', 'zoom_duration')
    def _onchange_zoom_user_id(self):
        if self.is_zoom_meeting and self.zoom_start_datetime and self.zoom_duration:
            res = self._get_list_zoom_user_available()
            if len(res) == 0:
                zoom_start_datetime = self.env['to.base'].convert_utc_time_to_tz(self.zoom_start_datetime)
                warning = {
                    'message': 'Zoom: All hosts have been used at %s. Please wait for the Administration to add the Host.' % zoom_start_datetime,
                }
                self._send_message_empty_host_email()
                return {'warning': warning}
            return {'domain': {'zoom_user_id': [('id', 'in', res)]}}

    def _get_list_user_of_group(self, group='to_zoom_calendar.group_admin'):
        '''List all users of group.'''
        user_ids = []
        group_system = self.env['ir.model.data'].xmlid_to_res_id(group)
        sql_query = """SELECT uid FROM res_groups_users_rel WHERE gid = %s"""
        params = (group_system,)
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.fetchall()
        for users_id in results:
            user_ids.append(users_id[0])
        return self.env['res.users'].search([('id', 'in', user_ids)])

    def _send_message_empty_host_email(self):
        '''Send notification email if all Zoom Hosts are empty.'''
        template = self.env.ref('to_zoom_calendar.zoom_template_notif_empty_host', raise_if_not_found=False)
        zoom_start_datetime = self.env['to.base'].convert_utc_time_to_tz(self.zoom_start_datetime)
        for uid in self._get_list_user_of_group():
            template.with_context(lang=uid.lang, zoom_start_datetime=zoom_start_datetime).send_mail(uid.id, force_send=True)

    def _get_list_zoom_user_available(self):
        result = []
        user_ids = self.env['zoom.user'].search([])
        for u in user_ids:
            res = self._check_zoom_user_id(u.zoom_email)
            if res:
                result.append(u.id)

        return result

    def _check_zoom_user_id(self, zoom_email, vals=False):
        """Check if there's any zoom at the same time"""
        zoom_apiv2 = self.env['zoom.apiv2']
        res = zoom_apiv2.get_meetings(zoom_email)
        result = res.json()
        if res.status_code == 200:
            if vals:
                zoom_start_datetime = fields.Datetime.to_datetime(vals.get('zoom_start_datetime', False)) or self.zoom_start_datetime
                zoom_duration = vals.get('zoom_duration', False) or self.zoom_duration
            else:
                zoom_start_datetime = self.zoom_start_datetime
                zoom_duration = self.zoom_duration

            zoom_end_datetime = zoom_start_datetime + datetime.timedelta(minutes=zoom_duration)
            for r in result.get('meetings'):
                start_date = fields.Datetime.to_datetime('%s %s' % (r.get('start_time')[:10], r.get('start_time')[11:19]))
                if start_date + datetime.timedelta(minutes=r.get('duration')) <= zoom_start_datetime or zoom_end_datetime <= start_date:
                    continue
                else:
                    if self.zoom_meeting_id == str(r.get('id')):
                        continue
                    return False

            page_number = result.get('page_number')
            page_count = result.get('page_count')

            if page_number < page_count:
                while page_number < page_count:
                    res = zoom_apiv2.get_meetings(zoom_email, page_number=page_number + 1)
                    result = res.json()
                    if res.status_code == 200:
                        for r in result.get('meetings'):
                            start_date = fields.Datetime.to_datetime('%s %s' % (r.get('start_time')[:10], r.get('start_time')[11:19]))
                            if start_date + datetime.timedelta(minutes=r.get('duration')) < zoom_start_datetime or zoom_end_datetime < start_date:
                                continue
                            else:
                                if self.zoom_meeting_id == str(r.get('id')):
                                    continue
                                return False
                    else:
                        return False
                    page_number += 1
            return True
        else:
            return False

    @api.onchange('is_zoom_meeting')
    def _onchange_is_zoom_meeting(self):
        if self.is_zoom_meeting and not self.zoom_meeting_id:
            zoom_user_id = self.env['zoom.user'].search([], limit=1)
            if zoom_user_id:
                self.zoom_user_id = zoom_user_id.id
            else:
                warning = {
                    'message': 'Please Configure Zoom Credentials',
                }
                return {'warning': warning}
            self.zoom_name = self.name
            self.zoom_start_datetime = self.start_datetime
            self.zoom_duration = self.duration * 60
            self.zoom_description = self.description
            self.zoom_recurrency = self.recurrency
            if self.recurrency and self.rrule_type in ['daily', 'weekly']:
                self.zoom_rrule_type = self.rrule_type
                self.zoom_interval = self.interval
                self.zoom_end_type = self.end_type
                if self.zoom_rrule_type == 'weekly':
                    self.zoom_su = self.su
                    self.zoom_mo = self.mo
                    self.zoom_tu = self.tu
                    self.zoom_we = self.we
                    self.zoom_th = self.th
                    self.zoom_fr = self.fr
                    self.zoom_sa = self.sa
                if self.zoom_end_type == 'count':
                    self.zoom_count = self.count
                    self.zoom_count = self.count
                else:
                    self.zoom_final_date = self.final_date

    @api.onchange('name')
    def _onchange_name(self):
        if self.is_zoom_meeting and not self.zoom_meeting_id:
            self.zoom_name = self.name

    @api.onchange('start_datetime')
    def _onchange_start_datetime(self):
        if self.is_zoom_meeting and not self.zoom_meeting_id:
            self.zoom_start_datetime = self.start_datetime

    @api.onchange('duration')
    def _onchange_duration(self):
        super(CalendarEvent, self)._onchange_duration()
        if self.is_zoom_meeting and not self.zoom_meeting_id:
            self.zoom_duration = self.duration * 60

    @api.onchange('description')
    def _onchange_description(self):
        if self.is_zoom_meeting and not self.zoom_meeting_id:
            self.zoom_description = self.description

    @api.onchange('recurrency', 'interval', 'rrule_type', 'count', 'end_type', 'final_date', 'mo', 'tu', 'th', 'we', 'fr', 'sa', 'su')
    def _onchange_recurrency(self):
        if self.is_zoom_meeting and not self.zoom_meeting_id:
            self.zoom_recurrency = self.recurrency
            if self.recurrency and self.rrule_type in ['daily', 'weekly']:
                self.zoom_rrule_type = self.rrule_type
                self.zoom_interval = self.interval
                self.zoom_end_type = self.end_type
                if self.zoom_rrule_type == 'weekly':
                    self.zoom_su = self.su
                    self.zoom_mo = self.mo
                    self.zoom_tu = self.tu
                    self.zoom_we = self.we
                    self.zoom_th = self.th
                    self.zoom_fr = self.fr
                    self.zoom_sa = self.sa
                if self.zoom_end_type == 'count':
                    self.zoom_count = self.count
                else:
                    self.zoom_final_date = self.final_date

    @api.depends('user_id')
    def _get_owner_zoom(self):
        users = [uid.id for uid in self._get_list_user_of_group()]
        for r in self:
            if self.env.user.id == r.user_id.id or self.env.user.id == r.create_uid.id or self.env.user.id in users:
                r.is_owner_zoom = True
            else:
                r.is_owner_zoom = False

    @api.model
    def _prepare_zoom_meeting_values(self, vals, zoom_setting, zoom_recurrency):
        """Prepare the dict of values to create the Zoom meeting"""
        settings = {}
        recurrences = {}

        data = {
            'password': str(randint(100000, 999999)),
            'timezone': 'UTC',  # To set a meeting’s start time using a UTC timezone
        }
        if vals.get('zoom_name', False):
            data.update({'topic': vals.get('zoom_name')})

        if vals.get('zoom_type', False):
            data.update({'type': vals.get('zoom_type')})

        if vals.get('zoom_start_datetime', False):
            # Ensure to zoom_start_datetime in vals used an UTC timezone
            # However, Odoo's the timezone default is an UTC timezone
            start_datetime = str(vals.get('zoom_start_datetime'))
            data.update({'start_time': '%sT%sZ' % (start_datetime[:10], start_datetime[11:19])})

        if vals.get('zoom_duration', False):
            data.update({'duration': vals.get('zoom_duration')})

        if vals.get('zoom_description', False):
            data.update({'agenda': vals.get('zoom_description')})

        if zoom_setting:
            if vals.get('zoom_setting_join_before_host', False):
                settings.update({'join_before_host': vals.get('zoom_setting_join_before_host')})

            if vals.get('zoom_setting_mute_upon_entry', False):
                settings.update({'mute_upon_entry': vals.get('zoom_setting_mute_upon_entry')})

            if vals.get('zoom_setting_approval_type', False):
                settings.update({'approval_type': vals.get('zoom_setting_approval_type')})

            if vals.get('zoom_setting_auto_recording', False):
                settings.update({'auto_recording': vals.get('zoom_setting_auto_recording')})

            data.update({'settings': settings})

        if zoom_recurrency:
            if vals.get('zoom_interval', False):
                recurrences.update({'repeat_interval': vals.get('zoom_interval')})

            if vals.get('zoom_rrule_type', False) == 'daily':
                recurrences.update({'type': 1})

            if vals.get('zoom_rrule_type', False) == 'weekly':
                weekly_days = ''
                if vals.get('zoom_su', False):
                    weekly_days += '1,'
                if vals.get('zoom_mo', False):
                    weekly_days += '2,'
                if vals.get('zoom_tu', False):
                    weekly_days += '3,'
                if vals.get('zoom_we', False):
                    weekly_days += '4,'
                if vals.get('zoom_th', False):
                    weekly_days += '5,'
                if vals.get('zoom_fr', False):
                    weekly_days += '6,'
                if vals.get('zoom_sa', False):
                    weekly_days += '7'
                recurrences.update({
                    'type': 2,
                    'weekly_days': weekly_days
                })

            if vals.get('zoom_end_type', False) == 'count':
                recurrences.update({'end_times': vals.get('zoom_count')})
            if vals.get('zoom_end_type', False) == 'end_date':
                recurrences.update({'end_date_time': vals.get('zoom_final_date')})

            data.update({'recurrence': recurrences})
        return data

    def create_zoom_meeting(self, vals):
        """This method to generate Zoom Meeting"""
        data = self._prepare_zoom_meeting_values(vals, vals.get('zoom_setting', False), vals.get('zoom_recurrency', False))
        zoom_apiv2 = self.env['zoom.apiv2']
        zoom_email = self.env['zoom.user'].search_read(
            [('id', '=', vals.get('zoom_user_id', self.zoom_user_id.id))],
            ['zoom_email'],
            limit=1
            )
        res = zoom_apiv2.create_meeting(zoom_email[0].get('zoom_email'), data)
        result = res.json()
        if res.status_code == 201:
            return result
        else:
            raise ValidationError('Zoom: %s' % result.get('message'))

    def update_zoom_meeting(self, vals):
        zoom_apiv2 = self.env['zoom.apiv2']
        zoom_setting = vals.get('zoom_setting', False) or self.zoom_setting
        zoom_recurrency = vals.get('zoom_recurrency', False) or self.zoom_recurrency
        data = self._prepare_zoom_meeting_values(vals, zoom_setting, zoom_recurrency)
        res = zoom_apiv2.update_meeting(self.zoom_meeting_id, data)
        if res.status_code == 204:
            res = zoom_apiv2.get_meeting(self.zoom_meeting_id)
            result = res.json()
            if res.status_code == 200:
                return result
            return True
        else:
            result = res.json()
            raise ValidationError('Zoom: %s' % result.get('message'))

    def delete_zoom_meeting(self):
        zoom_apiv2 = self.env['zoom.apiv2']
        res = zoom_apiv2.delete_meeting(self.zoom_meeting_id)
        if res.status_code == 204:
            return True
        else:
            result = res.json()
            # code == 3001, the meeting zoom was deleted
            if 'code' not in result or result['code'] != 3001:
                raise ValidationError('Zoom: %s' % result.get('message'))

    def _check_fields_of_zoom_in_vals(self, vals):
        """Checks if there is a value field representing the Zoom meeting, then returns True"""

        fields_of_zoom = ['zoom_name', 'zoom_type', 'zoom_start_datetime', 'zoom_duration',
                          'zoom_description', 'zoom_recurrency', 'zoom_interval', 'zoom_rrule_type',
                          'zoom_end_type', 'zoom_count', 'zoom_final_date', 'zoom_su', 'zoom_mo',
                          'zoom_tu', 'zoom_we', 'zoom_th', 'zoom_fr', 'zoom_sa', 'zoom_setting',
                          'zoom_setting_join_before_host', 'zoom_setting_mute_upon_entry', 'zoom_setting_approval_type',
                          'zoom_setting_auto_recording']
        for k in vals:
            if k in fields_of_zoom:
                return True
        return False

    @api.model
    def create(self, vals):
        res = super(CalendarEvent, self).create(vals)

        if vals.get('is_zoom_meeting', False):
            result = self.create_zoom_meeting(vals)
            if result:
                for r in res:
                    r.write(r._prepare_vals_to_join_meeting(result))
        if res:
            res.action_sendmail()

        return res

    def write(self, vals):
        res = super(CalendarEvent, self).write(vals)
        send_mail = False

        if 'is_zoom_meeting' in vals:
            if vals['is_zoom_meeting']:
                for r in self:
                    result = r.create_zoom_meeting(vals)
                    r.write(r._prepare_vals_to_join_meeting(result))
                send_mail = True
            else:
                record_to_delete = self.filtered(lambda r: r.zoom_meeting_id)
                record_to_delete.delete_zoom_meeting()
                record_to_delete.write(record_to_delete._prepare_vals_to_join_meeting({}))

        if self._check_fields_of_zoom_in_vals(vals):
            for r in self:
                if r.is_zoom_meeting and r.zoom_meeting_id: 
                    result = r.update_zoom_meeting(vals)
                    r.write(r._prepare_vals_to_join_meeting(result))
            send_mail = True

        if send_mail:
            self.action_sendmail()
        return res

    def unlink(self):
        for r in self:
            if r.zoom_meeting_id:
                r.delete_zoom_meeting()
        return super(CalendarEvent, self).unlink()

    @api.model
    def _prepare_vals_to_join_meeting(self, result):
        """
        This method to process result from Zoom before passing self.env['calendar.event'].write(vals) method
        :param result dict from Zoom
        :return dict of values for passing into self.env['calendar.event'].write(vals) method
            {
                'zoom_meeting_id': result.get('id', False),
                'zoom_meeting_attendee_url': result.get('join_url', False), 
                'zoom_meeting_start_url': result.get('start_url', False),
            }
        """
        return {
            'zoom_meeting_id': result.get('id', False),
            'zoom_meeting_attendee_url': result.get('join_url', False),
            'zoom_meeting_start_url': result.get('start_url', False),
            }
