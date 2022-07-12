from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ZoomUserReport(models.TransientModel):
    _name = "zoom.user.report"
    _description = "Generate Zoom User Report"
    
    start_date = fields.Date(
        'Start Date', required=True,
        default=(datetime.today() - relativedelta(
            days=datetime.date(
                datetime.today()).weekday())).strftime('%Y-%m-%d'))
    end_date = fields.Date(
        'End Date', required=True,
        default=(datetime.today() + relativedelta(days=30 - datetime.date(
            datetime.today()).weekday())).strftime('%Y-%m-%d'))

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for r in self:
            if r.end_date < r.start_date:
                raise ValidationError(_('End Date cannot be set before Start Date.'))
            elif r.end_date > (r.start_date + timedelta(days=30)):
                raise ValidationError(_("Select date range for a month!"))

    def gen_zoom_user_report(self):
        data = {}
        user_list = []
        
        zoom_apiv2 = self.env['zoom.apiv2']
        res = zoom_apiv2.get_report_users(self.start_date, self.end_date)
        result = res.json()
        if res.status_code == 200:
            data.update({
                "date_from": result.get('from'),
                "date_to": result.get('to'),
                'total_meetings': result.get('total_meetings'),
                'total_meeting_minutes': result.get('total_meeting_minutes'),
                })
            for r in result.get('users'):
                user_list.append({
                    'email': r.get('email'),
                    'meetings': r.get('meetings'),
                    'meeting_minutes': r.get('meeting_minutes'),
                    })
            
            page_count = r.get('page_count')
            page_number = r.get('page_number')
            if page_number < page_count:
                while page_number < page_count:
                    res = zoom_apiv2.get_report_users(self.start_date, self.end_date, page_number=page_number+1)
                    result = res.json()
                    if res.status_code == 200:
                        for r in result.get('users'):
                            user_list.append({
                                'email': r.get('email'),
                                'meetings': r.get('meetings'),
                                'meeting_minutes': r.get('meeting_minutes'),
                                })
                    else:
                        raise ValidationError('Zoom: %s' % result.get('message'))
                    page_number += 1
            data.update({'user_list': user_list})
            template = self.env.ref('to_zoom_calendar.zoom_user_report_template')
            return template.report_action(self, data=data)
            
        else:
            raise ValidationError('Zoom: %s' % result.get('message'))
        
