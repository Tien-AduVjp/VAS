from datetime import datetime, time
from odoo import models, fields, api
from odoo import tools


class HrLeaveDetail(models.Model):
    _name = 'hr.leave.detail'
    _description = "Time Off Details"
    _order = 'date_from desc'
    _auto = False

    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)

    date_from = fields.Datetime(string="Date From")
    date_to = fields.Datetime(string="Date To")
    date = fields.Date(string='Date')
    duration_days = fields.Float(string='Days')
    duration_hours = fields.Float(string='Hours')

    leave_id = fields.Many2one('hr.leave', string='Time Off', readonly=True)
    leave_type_id = fields.Many2one('hr.leave.type', string='Time Off Type', readonly=True)
    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('company', 'By Company'),
        ('department', 'By Department'),
        ('category', 'By Employee Tag')], string='Mode', readonly=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')], string='Status', readonly=True)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(HrLeaveDetail, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)
        to_remove = []
        for group_line in result:
            duration_days = 0
            duration_hours = 0
            if group_line.get('duration_days', False) or group_line.get('duration_hours', False):
                domain = group_line.get('__domain', []) or domain
                if domain:
                    leave_details = self.search(domain)
                    for line in leave_details:
                        if line.date_from.date() == line.date_to.date():
                            date_from = line.date_from
                            date_to = line.date_to
                        else:
                            date_from = datetime.combine(line.date, time.min)
                            date_to = datetime.combine(line.date, time.max)
                            if line.date_from.date() == line.date:
                                date_from = line.date_from
                            if line.date_to.date() == line.date:
                                date_to = line.date_to
                        duration_leave = line.employee_id._get_work_days_data_batch(date_from, date_to, compute_leaves=False)[line.employee_id.id]
                        duration_days += duration_leave['days']
                        duration_hours += duration_leave['hours']
                else:
                    leaves = self.search([]).leave_id
                    duration_days = sum(leaves.mapped('number_of_days'))
                    duration_hours = sum(leaves.mapped('number_of_hours_display'))
                group_line['duration_days'] = duration_days if duration_days else False
                group_line['duration_hours'] = duration_hours if duration_hours else False
                if not group_line['duration_hours']:
                    to_remove.append(group_line)
        for i in to_remove:
            result.remove(i)
        return result

    def _select(self):
        return """
        SELECT
            row_number() OVER(ORDER BY l.id, l.date_from,l.date_to) AS id,
            l.id AS leave_id,
            l.holiday_status_id AS leave_type_id,
            l.holiday_type,
            l.state,
            l.date_from,
            l.date_to,
            l.number_of_days as duration_days,
            l.number_of_days as duration_hours,
            l.employee_id,
            l.department_id,
            d AS date
        """

    def _from(self):
        return """
        FROM hr_leave AS l,
            LATERAL
                (SELECT d::date
                 FROM generate_series(
                    l.date_from::date,
                    l.date_to::date,
                    interval '1d') d) d
        """

    def _join(self):
        return """
        """

    def _where(self):
        return """
        """

    def _group_by(self):
        return """
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s AS (
        %s
        %s
        %s
        %s
        %s)
        """ % (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by()))
