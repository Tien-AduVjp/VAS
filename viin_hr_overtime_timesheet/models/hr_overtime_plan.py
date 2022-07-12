from odoo import models, fields, api


class HrOvertimePlan(models.Model):
    _inherit = 'hr.overtime.plan'

    recognition_mode = fields.Selection(selection_add=[('timesheet', 'Timesheet')])
    timesheet_match_ids = fields.One2many('overtime.plan.line.timesheet.match', 'overtime_plan_id', readonly=True)
    timesheet_ids = fields.Many2many('account.analytic.line', 'overtime_plan_timesheet_rel', 'overtime_plan_id', 'timesheet_id',
                                      string='Related Timesheet Entries', compute='_compute_timesheet_ids', store=True)
    matched_timesheet_hours = fields.Float(string='Matched Timesheet Hours', compute='_compute_matched_timesheet_hours', store=True)
    
    # project integration
    for_project_id = fields.Many2one('project.project', string='Project', help="The project for which this overtime plan is")
    project_required = fields.Boolean(related='reason_id.project_required')
    project_task_ids = fields.Many2many('project.task', 'hr_overtime_plan_project_task_rel', 'overtime_plan_id', 'task_id',
                                        string='Tasks', compute='_compute_project_task_ids', store=True)
    project_ids = fields.Many2many('project.project', 'hr_overtime_plan_project_project_rel', 'overtime_plan_id', 'project_id',
                                        string='Projects', compute='_compute_project_ids', store=True)
    
    @api.depends('line_ids.matched_timesheet_hours')
    def _compute_matched_timesheet_hours(self):
        for r in self:
            r.matched_timesheet_hours = sum(r.line_ids.mapped('matched_timesheet_hours'))

    @api.depends('timesheet_match_ids.overtime_plan_id')
    def _compute_timesheet_ids(self):
        for r in self:
            r.timesheet_ids = [(6, 0, r.timesheet_match_ids.mapped('timesheet_id').ids)]

    @api.depends('timesheet_ids.task_id')
    def _compute_project_task_ids(self):
        for r in self:
            r.project_task_ids = [(6, 0, r.timesheet_ids.task_id.ids)]

    @api.depends('recognition_mode', 'timesheet_ids.project_id', 'for_project_id')
    def _compute_project_ids(self):
        for r in self:
            projects = r.timesheet_ids.project_id
            if r.recognition_mode != 'timesheet':
                projects |= r.for_project_id
            r.project_ids = [(6, 0, projects.ids)]

    def _match_timesheet_entries(self):
        self.line_ids._match_timesheet_entries()

    def action_match_timesheet_entries(self):
        self._match_timesheet_entries()

    def _recognize_actual_overtime(self):
        super(HrOvertimePlan, self)._recognize_actual_overtime()
        self._match_timesheet_entries()
