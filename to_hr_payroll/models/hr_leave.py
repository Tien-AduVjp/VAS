from odoo import models, fields, _
from odoo.exceptions import UserError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    payslip_status = fields.Boolean(tracking=True)

    def _remove_resource_leave(self):
        """ This override ensures no resource calendar leave will be removed if it is reported in by payslip"""
        all_resource_leaves = self.env['resource.calendar.leaves'].search([('holiday_id', 'in', self.ids)])
        to_del_working_month_calendars = self.env['hr.working.month.calendar'].sudo()
        to_recompute_payslips = self.env['hr.payslip'].sudo()
        for r in self:
            working_month_calendars = all_resource_leaves.filtered(
                lambda res: res.holiday_id == r
                ).sudo().payslip_leave_interval_ids \
                .working_month_calendar_line_id \
                .working_month_calendar_id
            if r.payslip_status:
                payslip = working_month_calendars.payslip_id[:1]
                if payslip:
                    raise UserError(_("Could not remove the resource leave related to the time off '%s' while it is still referred"
                                      " by the payslip '%s'. Please cancel the payslip first.")
                                      % (r.display_name, payslip.display_name))
                else:
                    raise UserError(_("Could not remove the resource leave related to the time off '%s' while it is marked as"
                                      " Reported in last payslips.")
                                      % r.display_name)
            to_del_working_month_calendars |= working_month_calendars
        # remove related working month calendar records
        if to_del_working_month_calendars:
            to_recompute_payslips |= to_del_working_month_calendars.payslip_id.filtered(lambda ps: ps.state == 'draft')
            to_del_working_month_calendars.unlink()

        res = super(HrLeave, self)._remove_resource_leave()
        # recompute related draft payslips
        to_recompute_payslips.compute_sheet()
        return res

    def _get_domain_payslip(self, employee, date1, date2):
        return [
            ('company_id', '=', self.env.company.id),
            ('employee_id', '=', employee.id),
            ('date_from', '<=', date1),
            ('date_to', '>=', date2),
            ('state', '!=', 'cancel')
        ]

    def _adjust_dates(self, date_from, date_to):
        HrPayslip = self.env['hr.payslip']
        # check condition to can adjustment
        domain = self._get_domain_payslip(self.employee_id, self.date_to.date(), self.date_from.date())
        payslip = HrPayslip.search(domain, order='date_to desc', limit=1)
        if payslip:
            if date_from != self.date_from:
                raise UserError(_("Can't adjust Date From because there is a payslip (%s) related to this leave") % payslip.name)

            if payslip.date_to >= self.date_to.date():
                raise UserError(_("Can't adjust Date To because there is a payslip (%s) related to this leave") % payslip.name)
            else:
                if date_to.date() < payslip.date_to:
                    raise UserError(_("Can't adjust the 'Date To' into within the payslip period (%s)") % payslip.name)
#                 elif date_to.date() == payslip.date_to:
#                     if leave type mode != day

        # check values after adjustment
        if self.date_to != date_to:
            domain = self._get_domain_payslip(self.employee_id, date_to.date(), self.date_to.date())
            payslip = HrPayslip.search(domain, limit=1)
            if payslip:
                raise UserError(_("Can't adjust the 'Date To' into within the payslip period (%s)") % payslip.name)
        if self.date_from != date_from:
            domain = self._get_domain_payslip(self.employee_id, self.date_from.date(), date_from.date())
            payslip = HrPayslip.search(domain, limit=1)
            if payslip:
                raise UserError(_("Can't adjust the 'Date From' into within the payslip period (%s)") % payslip.name)

        super(HrLeave, self)._adjust_dates(date_from, date_to)
