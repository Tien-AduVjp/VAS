from odoo import models


class HrPayslipContributionLine(models.Model):
    _inherit = 'hr.payslip.contribution.line'

    def _get_paid_days(self, contract, res_calendar_datas):
        if contract.salary_attendance_computation_mode == 'attendance':
            paid_days = 0
            for start, end, res_calendar in res_calendar_datas:
                paid_days += self._get_attendance_days(start, end, res_calendar)
            return paid_days
        else:
            return super(HrPayslipContributionLine, self)._get_paid_days(contract, res_calendar_datas)

    def _get_attendance_days(self, start, end, res_calendar):
        payslip_attendances = self.payslip_id.attendance_ids
        attendances = payslip_attendances.filtered(
            lambda att: att.check_in >= start and att.check_out <= end
        )
        valid_attendance_hours = sum(attendances.mapped('valid_worked_hours'))
        attendance_days = valid_attendance_hours / res_calendar.hours_per_day
        return attendance_days
