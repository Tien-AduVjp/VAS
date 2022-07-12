from datetime import datetime, time

from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    overtime_plan_line_ids = fields.Many2many('hr.overtime.plan.line', 'overtime_plan_line_hr_payslip_rel', 'payslip_id', 'plan_line_id',
                                                       string='Overtime Plan Lines', compute='_compute_overtime_plan_line_ids', store=True)
    overtime_plan_lines_count = fields.Integer(string='Overtime Entries Count', compute='_compute_overtime_plan_lines_count')

    @api.depends('date_from', 'date_to', 'employee_id', 'state',
                 'employee_id.overtime_plan_ids',
                 'employee_id.overtime_plan_ids.date_start',
                 'employee_id.overtime_plan_ids.date_end',
                 'employee_id.overtime_plan_ids.line_ids')
    def _compute_overtime_plan_line_ids(self):
        draft_payslips = self.filtered(lambda r:r.state == 'draft')
        if draft_payslips:
            plan_lines = draft_payslips._get_overtime_entries()
            for r in draft_payslips:
                lines = self.env['hr.overtime.plan.line']
                if r.employee_id and r.date_from and r.date_to:
                    date_end = datetime.combine(r.date_to, time.max)
                    lines = plan_lines.filtered(lambda l: \
                                                l.employee_id == r.employee_id \
                                                and l.overtime_plan_id.currency_id == r.currency_id \
                                                and l.date_end <= date_end
                                                )
                r.overtime_plan_line_ids = [(6, 0, lines.ids)]
        for r in self - draft_payslips:
            r.overtime_plan_line_ids = r.overtime_plan_line_ids

    def _compute_overtime_plan_lines_count(self):
        for r in self:
            r.overtime_plan_lines_count = len(r.overtime_plan_line_ids)

    def _get_overtime_entries_domain(self):
        sorted_payslips = self.sorted_by_dates(reverse=False)
        date_end = datetime.combine(sorted_payslips[-1:].date_to, time.max) if sorted_payslips else fields.Datetime.now()
        return [
            ('employee_id', 'in', self.mapped('employee_id').ids),
            ('date_end', '<=', date_end),
            ('actual_hours', '>', 0.0)
            ]

    def _get_overtime_entries(self):
        plan_lines = self.env['hr.overtime.plan.line'].search(self._get_overtime_entries_domain())
        return plan_lines.filtered(lambda r: not r.has_non_draft_payslips)

    def _recognize_actual_overtime(self):
        self.employee_id.overtime_plan_line_ids.mapped('overtime_plan_id')._recognize_actual_overtime()

    def _recompute_fields(self):
        super(HrPayslip, self)._recompute_fields()
        self._compute_overtime_plan_line_ids()

    def action_compute_overtime_plan_line_ids(self):
        self._compute_overtime_plan_line_ids()
        self._recognize_actual_overtime()

    def action_view_overtime_plan_lines(self):
        result = self.env['ir.actions.actions']._for_xml_id('viin_hr_overtime.action_hr_overtime_plan_line')
        # override the context to get rid of the default filtering
        result['context'] = {'search_default_grp_rule':1}
        result['domain'] = "[('payslip_ids','in',%s)]" % str(self.ids)
        return result
