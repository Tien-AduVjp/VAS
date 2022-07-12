from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    project_id = fields.Many2one('project.project', string='Project', tracking=True, compute='_compute_project_id', store=True, readonly=False,
                                 inverse='_inverse_project_id',
                                 help="Project which the helpdesk tickets and timesheets will be used.")
    task_id = fields.Many2one('project.task', string='Task', domain="[('project_id', '=', project_id)]", tracking=True,
                                 help="Task which the helpdesk tickets and timesheets will be used.")
    use_helpdesk_timesheet = fields.Boolean(string='Timesheet on Tickets', related='project_id.allow_timesheets', store=True)
    timesheet_ids = fields.One2many('account.analytic.line', 'ticket_id', string='Timesheets', groups='hr_timesheet.group_hr_timesheet_user')

    def write(self, vals):
        if not self.env.user.has_group('viin_helpdesk.group_helpdesk_manager') and len(vals) == 1 and 'timesheet_ids' in vals:
            self = self.sudo()
        return super(HelpdeskTicket, self).write(vals)

    @api.depends('team_id', 'task_id.project_id')
    def _compute_project_id(self):
        for r in self:
            if r.task_id.project_id:
                r.project_id = r.task_id.project_id
            else:
                r.project_id = r.team_id.project_id
    
    def _inverse_project_id(self):
        for r in self:
            if not r.project_id:
                r.task_id = False
