from odoo import models, fields, api


class HrOvertimePlanLine(models.Model):
    _inherit = 'hr.overtime.plan.line'
    
    recognition_mode = fields.Selection(selection_add=[('timesheet', 'Timesheet')])
    timesheet_ids = fields.Many2many('account.analytic.line', 'hr_overtime_plan_line_timesheet_rel', 'overtime_plan_line_id', 'timesheet_id',
                                      string='Related Timesheet Entries', readonly=True)
    timesheet_match_ids = fields.One2many('overtime.plan.line.timesheet.match', 'overtime_plan_line_id',
                                           string='Timesheet Match', compute='_compute_timesheet_match_ids', store=True)
    matched_timesheet_hours = fields.Float(string='Matched Timesheet Hours', compute='_compute_matched_timesheet_hours', store=True)
    unmatched_timesheet_hours = fields.Float(string='Unmatched Timesheet Hours', compute='_compute_unmatched_timesheet_hours', store=True)
    
    # project integration
    project_task_ids = fields.Many2many('project.task', 'hr_overtime_plan_line_project_task_rel', 'overtime_plan_line_id', 'task_id',
                                        string='Tasks', compute='_compute_project_task_ids', store=True)
    project_ids = fields.Many2many('project.project', 'hr_overtime_plan_line_project_project_rel', 'overtime_plan_line_id', 'project_id',
                                        string='Projects', compute='_compute_project_ids', store=True)

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        records = super(HrOvertimePlanLine, self).create(vals_list)
        records._match_timesheet_entries()
        return records

    def write(self, vals):
        res = super(HrOvertimePlanLine, self).write(vals)
        if any(f in vals for f in self._get_fields_to_trigger_timesheet_match_update()):
            self._match_timesheet_entries()
        return res
    
    def _get_fields_to_trigger_timesheet_match_update(self):
        return self._get_fields_to_trigger_match_update()

    @api.depends('timesheet_ids', 'timesheet_ids.date_start', 'timesheet_ids.date_end')
    def _compute_timesheet_match_ids(self):
        for r in self:
            cmd = [(3, line.id) for line in r.timesheet_match_ids]
            vals_list = r._prepare_timesheet_match_vals_list()
            cmd += [(0, 0, vals) for vals in vals_list]
            r.timesheet_match_ids = cmd

    @api.depends('timesheet_match_ids.matched_hours')
    def _compute_matched_timesheet_hours(self):
        for r in self:
            r.matched_timesheet_hours = sum(r.timesheet_match_ids.mapped('matched_hours'))

    @api.depends('timesheet_match_ids.unmatched_hours')
    def _compute_unmatched_timesheet_hours(self):
        for r in self:
            r.unmatched_timesheet_hours = sum(r.timesheet_match_ids.mapped('unmatched_hours'))

    @api.depends('matched_timesheet_hours')
    def _compute_actual_hours(self):
        super(HrOvertimePlanLine, self)._compute_actual_hours()
        for r in self:
            if r.recognition_mode == 'timesheet':
                r.actual_hours = r.matched_timesheet_hours

    @api.depends('timesheet_ids.task_id')
    def _compute_project_task_ids(self):
        for r in self:
            r.project_task_ids = [(6, 0, r.timesheet_ids.task_id.ids)]

    @api.depends('recognition_mode', 'timesheet_ids.project_id', 'overtime_plan_id.for_project_id')
    def _compute_project_ids(self):
        for r in self:
            projects = r.timesheet_ids.project_id
            if r.recognition_mode != 'timesheet':
                projects |= r.overtime_plan_id.for_project_id
            r.project_ids = [(6, 0, projects.ids)]

    def _match_timesheet_entries(self):
        related_timesheet_entries = self._get_related_timesheet_entries()
        for r in self:
            matched_entries = related_timesheet_entries.filtered(
                lambda att: att.employee_id == r.employee_id \
                and att.date_start < r.date_end \
                and att.date_end > r.date_start
                )
            r.timesheet_ids = [(6, 0, matched_entries.ids)]

    def _get_related_timesheet_entries(self):
        return self.env['account.analytic.line'].sudo().search(self._get_related_timesheet_domain())

    def _get_related_timesheet_domain(self):
        sorted_lines = self.sorted('date_start')
        return [
            ('employee_id', 'in', sorted_lines.with_context(active_test=False).mapped('employee_id').ids),
            ('project_id', '!=', False),
            ('date_start', '!=', False),
            ('date_end', '!=', False),
            ('date_start', '<', sorted_lines[-1:].date_end),
            ('date_end', '>', sorted_lines[:1].date_start)
            ]
    
    def action_match_timesheet_entries(self):
        self._match_timesheet_entries()

    def _prepare_timesheet_match_vals_list(self):
        vals_list = []
        for r in self:
            for timesheet in r.timesheet_ids:
                date_start, date_end = r._get_match_intervals(timesheet.date_start, timesheet.date_end)
                if not date_start or not date_end:
                    continue
                vals_list.append({
                    'timesheet_id': timesheet.id,
                    'overtime_plan_line_id': r.id,
                    'overtime_plan_id': r.overtime_plan_id.id,
                    'date_start': date_start,
                    'date_end': date_end
                    })
        return vals_list
        
