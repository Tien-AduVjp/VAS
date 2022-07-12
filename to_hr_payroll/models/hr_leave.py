from datetime import datetime
from odoo import models, _
from odoo.exceptions import UserError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _remove_resource_leave(self):
        """ This override ensures no resource calendar leave will be removed if it is referred by payslip"""
        all_resource_leaves = self.env['resource.calendar.leaves'].search([('holiday_id', 'in', self.ids)])
        for r in self:
            for resource_leave in all_resource_leaves.filtered(lambda res: res.holiday_id == r):
                for payslip in resource_leave.sudo().payslip_leave_interval_ids.working_month_calendar_line_id.working_month_calendar_id.payslip_id:
                    raise UserError(_("Could not remove the resource leave related to the time off '%s' while it is still referred"
                                      " by the payslip '%s'. Please delete the payslip first.")
                                      % (r.display_name, payslip.display_name))
        return super(HrLeave, self)._remove_resource_leave()
    
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
                raise UserError(_("Can't adjust Date From because there is a payslip (%s) related to this leave")%payslip.name)
            
            if payslip.date_to >= self.date_to.date():
                raise UserError(_("Can't adjust Date To because there is a payslip (%s) related to this leave")%payslip.name)
            else:
                if date_to.date() < payslip.date_to:
                    raise UserError(_("Can't adjust the 'Date To' into within the payslip period (%s)")%payslip.name)
#                 elif date_to.date() == payslip.date_to:
#                     if leave type mode != day
        
        # check values after adjustment
        if self.date_to != date_to:
            domain = self._get_domain_payslip(self.employee_id, date_to.date(), self.date_to.date())
            payslip = HrPayslip.search(domain, limit=1)
            if payslip:
                raise UserError(_("Can't adjust the 'Date To' into within the payslip period (%s)")%payslip.name)
        if self.date_from != date_from:
            domain = self._get_domain_payslip(self.employee_id, self.date_from.date(), date_from.date())
            payslip = HrPayslip.search(domain, limit=1)
            if payslip:
                raise UserError(_("Can't adjust the 'Date From' into within the payslip period (%s)")%payslip.name)
        
        super(HrLeave, self)._adjust_dates(date_from, date_to)
