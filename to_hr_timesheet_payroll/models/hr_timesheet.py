from odoo import models, api, _
from odoo.exceptions import UserError
from odoo.tools import format_date


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _recompute_related_payslips(self):
        hr_timesheet_lines = self.filtered(lambda r: r.project_id and r.employee_id)

        payslips = self.env['hr.payslip'].sudo()
        for employee in hr_timesheet_lines.mapped('employee_id'):
            timesheet_lines = hr_timesheet_lines.filtered(lambda l: l.employee_id == employee)
            earliest_date = min(timesheet_lines.mapped('date'))
            latest_date = max(timesheet_lines.mapped('date'))
            payslips |= payslips.search([
                ('date_from', '<=', latest_date),
                ('date_to', '>=', earliest_date),
                ('employee_id', '=', employee.id)]).sudo()
        if payslips:
            for payslip in payslips:
                if payslip.state not in ('draft', 'cancel'):
                    raise UserError(_("You may not log timesheet for the period %s - %s while the status of the corresponding payslip"
                                      " '%s' is neither Draft nor Cancelled. Please ask your Payroll Managers to set the payslip"
                                      " to either draft or cancelled first.")
                                      % (
                                          format_date(payslip.env, payslip.date_from),
                                          format_date(payslip.env, payslip.date_to),
                                          payslip.display_name
                                          ))
            payslips._compute_timesheet_lines()

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AccountAnalyticLine, self).create(vals_list)
        # attempt to add new timesheet to existing payslips
        records._recompute_related_payslips()
        return records

    @api.model
    def _get_protected_fields_by_payslips(self):
        '''
        Returns list of fields that will not be able to edit as soon as the timesheet
        records are referred by payslips.
        '''
        return ['employee_id', 'amount', 'task_id', 'project_id', 'date']

    def write(self, vals):
        protected_fields = self._get_protected_fields_by_payslips()
        if any(field_name in protected_fields for field_name in vals.keys()):
            payslips = self.env['hr.payslip'].sudo().search([('timesheet_line_ids', 'in', self.ids)])
            if payslips and not self._context.get('ignore_payslip_state_check', False):
                for payslip in payslips.sudo():
                    if payslip.state not in ('draft', 'cancel'):
                        raise UserError(_("You may not edit timesheet for the period %s - %s while the status of the corresponding payslip"
                                          " '%s' is neither Draft nor Cancelled. Please ask your Payroll Managers to set"
                                          " the payslip to either draft or cancelled first.")
                                          % (
                                            format_date(payslip.env, payslip.date_from),
                                            format_date(payslip.env, payslip.date_to),
                                            payslip.display_name
                                            ))
        return super(AccountAnalyticLine, self).write(vals)

    def unlink(self):
        payslips = self.env['hr.payslip'].sudo()
        payslips |= payslips.search([('timesheet_line_ids', 'in', self.ids)])
        for payslip in payslips:
            if payslip.state not in ('draft', 'cancel'):
                raise UserError(_("You may not delete timesheet for the period %s - %s while the status of the corresponding payslip"
                                  " '%s' is neither Draft nor Cancelled. Please ask your Payroll Managers to set the payslip to"
                                  " either draft or cancelled first.")
                                  % (
                                      format_date(payslip.env, payslip.date_from),
                                      format_date(payslip.env, payslip.date_to),
                                      payslip.display_name
                                      ))
        return super(AccountAnalyticLine, self).unlink()

