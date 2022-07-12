import datetime
from random import randint
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    zoom_meeting_id = fields.Char(string='Zoom Meeting Id')
    zoom_user_id = fields.Many2one('zoom.user', string='Zoom Meeting Host',
                                   domain=lambda self: self._get_list_zoom_user_available(), help='This is host ID for the meeting.')
    zoom_type = fields.Selection([
        ('1', 'Instant meeting'),
        ('2', 'Scheduled'),
        ('3', 'Recurring meeting with no fixed time'),
        ('8', 'Recurring meeting with fixed time')],
        string='Meeting Type',
        default='2', required=True)

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

    @api.constrains('zoom_user_id', 'duration', 'start')
    def _constrains_zoom_user_id(self):
        to_base = self.env['to.base']
        for r in self:
            if r.is_zoom_meeting and not r._check_zoom_user_id(r.zoom_user_id.zoom_email):
                zoom_start_datetime = to_base.convert_utc_time_to_tz(r.start)
                raise UserError(_('Zoom: Host that you selected that have been used at %s. Please wait for the Administration to add the Host.') % zoom_start_datetime)

    @api.onchange('start', 'duration')
    def _onchange_zoom_user_id(self):
        if self.is_zoom_meeting and self.start and self.duration:
            res = self._get_list_zoom_user_available()
            if len(res) == 0:
                zoom_start_datetime = self.env['to.base'].convert_utc_time_to_tz(self.start)
                warning = {
                    'message': 'Zoom: All hosts have been used at %s. Please wait for the Administration to add the Host.' % zoom_start_datetime,
                }
                self._send_message_empty_host_email()
                return {'warning': warning}

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
        if self.is_zoom_meeting:
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
                zoom_start_datetime = fields.Datetime.to_datetime(vals.get('start', False)) or self.start
                zoom_duration = (vals.get('duration', 0) or self.duration) * 60
            else:
                zoom_start_datetime = self.start or fields.datetime.now()
                zoom_duration = self.duration * 60

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

    @api.depends('user_id')
    def _get_owner_zoom(self):
        users = [uid.id for uid in self._get_list_user_of_group()]
        for r in self:
            if self.env.user.id == r.user_id.id or self.env.user.id == r.create_uid.id or self.env.user.id in users:
                r.is_owner_zoom = True
            else:
                r.is_owner_zoom = False

    def _prepare_zoom_meeting_values(self):
        """Prepare the dict of values to create/update the Zoom meeting"""
        self.ensure_one()

        settings = {}
        recurrences = {}

        data = {
            'password': str(randint(100000, 999999)),
            'timezone': 'UTC',  # To set a meeting’s start time using a UTC timezone
        }

        data.update({
            'topic': self.name,
            'agenda': self.description,
            'type': self.zoom_type,
            })

        # Ensure to zoom_start_datetime in vals used an UTC timezone
        # However, Odoo's the timezone default is an UTC timezone
        if self.allday:
            start_datetime = datetime.datetime.combine(self.start_date, datetime.time.min)
            stop_datetime = datetime.datetime.combine(self.stop_date, datetime.time.max)

            data.update({
                'start_time': '%sT00:00:00Z' % str(self.start_date),
                # duration is in minus
                # and from 00:00 of start date to 23h:59 of stop date
                'duration': int((stop_datetime - start_datetime).total_seconds() / 60),  # in minus

                })
        else:
            if self.start:
                start_datetime = str(self.start)
                data.update({'start_time': '%sT%sZ' % (start_datetime[:10], start_datetime[11:19])})
            if self.duration:
                data.update({'duration': self.duration * 60})  # in minus

        if self.zoom_setting:
            if self.zoom_setting_join_before_host:
                settings.update({'join_before_host': self.zoom_setting_join_before_host})

            if self.zoom_setting_mute_upon_entry:
                settings.update({'mute_upon_entry': self.zoom_setting_mute_upon_entry})

            if self.zoom_setting_approval_type:
                settings.update({'approval_type': self.zoom_setting_approval_type})

            if self.zoom_setting_auto_recording:
                settings.update({'auto_recording': self.zoom_setting_auto_recording})

            data.update({'settings': settings})

        if self.recurrency:
            if self.interval:
                recurrences.update({'repeat_interval': self.interval})

            if self.rrule_type == 'daily':
                recurrences.update({'type': 1})
            elif self.rrule_type == 'monthly':
                recurrences.update({'type': 3})
            elif self.rrule_type == 'weekly':
                weekly_days = ''
                if self.su:
                    weekly_days += '1,'
                if self.mo:
                    weekly_days += '2,'
                if self.tu:
                    weekly_days += '3,'
                if self.we:
                    weekly_days += '4,'
                if self.th:
                    weekly_days += '5,'
                if self.fr:
                    weekly_days += '6,'
                if self.sa:
                    weekly_days += '7'
                recurrences.update({
                    'type': 2,
                    'weekly_days': weekly_days
                })

            if self.end_type == 'count':
                recurrences.update({'end_times': self.count})
            elif self.end_type == 'end_date':
                recurrences.update({'end_date_time': self.final_date})
            elif self.end_type == 'forever':
                raise ValidationError(_("Zoom meeting with forever repeat doesn't support!"))

            if recurrences:
                data.update({'recurrenceValues': recurrences})
        return data

    def create_zoom_meeting(self):
        """This method to generate Zoom Meeting"""
        self.ensure_one()

        data = self._prepare_zoom_meeting_values()
        zoom_apiv2 = self.env['zoom.apiv2']
        zoom_email = self.env['zoom.user'].search_read([('id', '=', self.zoom_user_id.id)], ['zoom_email'], limit=1)

        res = zoom_apiv2.create_meeting(zoom_email[0].get('zoom_email'), data)
        result = res.json()
        if res.status_code == 201:
            return result
        else:
            raise ValidationError('Zoom: %s' % result.get('message'))

    def update_zoom_meeting(self):
        self.ensure_one()

        zoom_apiv2 = self.env['zoom.apiv2']
        data = self._prepare_zoom_meeting_values()
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

    @api.model
    def _check_fields_of_zoom_in_vals(self, vals):
        """Checks if there is a value field representing the Zoom meeting, then returns True"""

        fields_of_zoom = [
            'name', 'zoom_type', 'start', 'duration',
            'description', 'recurrency', 'interval', 'rrule_type',
            'end_type', 'count', 'final_date',
            'su', 'mo', 'tu', 'we', 'th', 'fr', 'sa',
            'zoom_setting',
            'zoom_setting_join_before_host',
            'zoom_setting_mute_upon_entry',
            'zoom_setting_approval_type',
            'zoom_setting_auto_recording',
            ]

        for k in vals:
            if k in fields_of_zoom:
                return True
        return False

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        res = super(CalendarEvent, self).create(vals_list)

        for r in res.filtered(lambda  r: r.is_zoom_meeting):
            result = r.create_zoom_meeting()
            if result:
                for r in res:
                    r.write(r._prepare_vals_to_join_meeting(result))
        if res:
            res.action_sendmail()

        return res

    def write(self, vals):
        res = super(CalendarEvent, self).write(vals)

        records_to_notif = self.env['calendar.event']


        if 'is_zoom_meeting' in vals:
            if vals['is_zoom_meeting']:
                for r in self.filtered(lambda r: r.is_zoom_meeting):
                    result = r.create_zoom_meeting()
                    r.write(r._prepare_vals_to_join_meeting(result))

                    records_to_notif |= r
            else:
                record_to_delete = self.filtered(lambda r: r.zoom_meeting_id)
                record_to_delete.delete_zoom_meeting()
                record_to_delete.write(record_to_delete._prepare_vals_to_join_meeting({}))

        if self._check_fields_of_zoom_in_vals(vals):
            for r in self.filtered(lambda r: r.is_zoom_meeting and r.zoom_meeting_id):
                result = r.update_zoom_meeting()
                r.write(r._prepare_vals_to_join_meeting(result))

                records_to_notif |= r

        if records_to_notif:
            records_to_notif.action_sendmail()
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
