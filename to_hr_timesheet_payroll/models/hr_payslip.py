from datetime import date

from odoo import models, fields, api
from odoo.osv import expression


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    timesheet_line_ids = fields.Many2many('account.analytic.line', 'hr_payslip_timesheet_line_rel', 'payslip_id', 'timesheet_line_id',
                                          string='Timesheet', compute='_compute_timesheet_lines', store=True)
    timesheet_lines_count = fields.Integer(string='Timesheet Lines Count', compute='_compute_timesheet_lines_count')
    timesheet_cost = fields.Monetary(string="Timesheet Cost", compute='_compute_timesheet_cost', store=True,
                                     help="The cost for timesheet log which is calculated based on the following formula:\n"
                                     "timesheet_cost = (company_cost / duty_working_hours) * general_overhead * total_timesheet_hours")
    total_timesheet_hours = fields.Float('Total Timesheet Hours', compute='_compute_total_timesheet_hours', default=0.0, compute_sudo=True)

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_timesheet_lines(self):
        self._load_timesheets()

    def _compute_timesheet_lines_count(self):
        for r in self:
            r.timesheet_lines_count = len(r.timesheet_line_ids)

    def _calculate_timesheet_hours(self):
        return sum(self.timesheet_line_ids.mapped('unit_amount'))

    @api.depends('timesheet_line_ids.unit_amount')
    def _compute_total_timesheet_hours(self):
        for r in self:
            r.total_timesheet_hours = r._calculate_timesheet_hours()
    
    def _update_employee_timesheet_cost(self):
        costs = self._calculate_payslip_timesheet_hour_cost()
        for r in self.filtered(lambda ps: ps.struct_id.update_employee_timesheet_cost).sorted_by_dates():
            r.employee_id.write({'timesheet_cost': costs.get(r, 0.0)})

    def _update_timesheet_lines_cost(self):
        """
        This method update the field amount of all the timesheet lines within
        the payslip period to reflect the new timesheet hour cost provided
        by the payslip.
        """
        all_timesheet_lines = self._get_timesheets(include_leaves=False)
        costs = self._calculate_payslip_timesheet_hour_cost()
        for r in self.filtered(lambda ps: ps.struct_id.update_employee_timesheet_cost).sorted(lambda ps: ps.date_to):
            timesheet_lines = all_timesheet_lines.filtered(
                lambda l: l.date >= r.date_from and l.date <= r.date_to and l.employee_id == r.employee_id \
                # if `sale_timesheet` module is installed, timesheet lines
                # will have `timesheet_invoice_id` field, and we should not
                # update the lines which are already invoiced
                and not (hasattr(l, 'timesheet_invoice_id') and l.timesheet_invoice_id)
                )
            for line in timesheet_lines.with_context(ignore_payslip_state_check=True):
                line.amount = -1 * costs.get(r, 0.0) * line.unit_amount

    def action_payslip_verify(self):
        res = super(HrPayslip, self).action_payslip_verify()
        # do NOT update timesheet if the payslip is a 13th month pay
        non_13thmonth_payslips = self.filtered(lambda ps: not ps.thirteen_month_pay)
        # do NOT update employee's timesheet_cost if the payslip is for backdate
        for employee in non_13thmonth_payslips.with_context(active_test=False).mapped('employee_id'):
            last_payslip = employee._get_last_payslip()
            to_process = non_13thmonth_payslips.filtered(lambda ps: ps.employee_id == employee).sorted_by_dates()
            if to_process[-1:].date_to < last_payslip.date_to:
                continue
            else:
                to_process._update_employee_timesheet_cost()
        non_13thmonth_payslips._update_timesheet_lines_cost()
        return res

    def _calculate_payslip_timesheet_hour_cost(self):
        costs = {}
        for r in self:
            if r.thirteen_month_pay:
                last_payslip = r._get_payslips_for_13thmonth()[-1:]
            else:
                last_payslip = r
            costs[r] = (last_payslip.company_cost / last_payslip.duty_working_hours) * last_payslip.company_id.general_overhead if last_payslip.duty_working_hours else 0.0
        return costs

    @api.depends('company_cost', 'duty_working_hours', 'timesheet_line_ids.unit_amount')
    def _compute_timesheet_cost(self):
        costs = self._calculate_payslip_timesheet_hour_cost()
        for r in self:
            r.timesheet_cost = costs.get(r, 0.0) * r._calculate_timesheet_hours()

    def action_view_timesheet(self):
        timesheet_line_ids = self.mapped('timesheet_line_ids')
        action = self.env.ref('hr_timesheet.timesheet_action_all')
        result = action.read()[0]
        # override the context to get rid of the default filtering
        result['context'] = {}
        result['domain'] = "[('id', 'in', %s)]" % str(timesheet_line_ids.ids)
        return result

    def _get_timesheets_domain(self, include_leaves=True):
        if not self.mapped('date_from'):
            return []
        earliest_date = min(self.mapped('date_from'))
        latest_date = max(self.mapped('date_to') or [fields.Date.today()])
        domain = self.mapped('employee_id')._get_timesheets_domain(earliest_date, latest_date, include_leaves)
        domain += expression.AND([domain, [('unit_amount', '!=', 0.0)]])
        return domain

    def _get_timesheets(self, include_leaves=False):
        date_from_list = self.mapped('date_from')
        # return empty timesheet recordset if non of payslips in self having `date_from` specified
        if not date_from_list:
            return self.env['account.analytic.line']
        return self.env['account.analytic.line'].sudo().search(self._get_timesheets_domain(include_leaves))

    def _load_timesheets(self):
        all_timsheet_lines = self._get_timesheets()
        for r in self:
            timsheet_lines = all_timsheet_lines.filtered(lambda l: l.employee_id == r.employee_id and l.date >= r.date_from and l.date <= r.date_to)
            contracts = r.contract_ids.filtered(lambda c: c.state in ['open', 'close'])
            valid_timesheets = self.env['account.analytic.line']
            for c in contracts:
                valid_timesheets |= timsheet_lines.filtered(lambda l: l.date >= c.date_start and l.date <= (c.date_end or date.max))
            r.timesheet_line_ids = [(6, 0, valid_timesheets.ids)]

    def action_load_timesheets(self):
        self._load_timesheets()
