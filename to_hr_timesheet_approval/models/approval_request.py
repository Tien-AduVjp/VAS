from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    timesheet_line_ids = fields.One2many('account.analytic.line', 'approval_id',
                                         string='Timesheets',
                                         compute='_compute_timesheet_lines',
                                         store=True,
                                         readonly=False,
                                         groups='hr_timesheet.group_hr_timesheet_user')

    @api.constrains('approval_type_id', 'timesheet_line_ids')
    def check_timesheet_type(self):
        for r in self:
            if r.timesheet_line_ids and r.approval_type_id.type != 'timesheets':
                raise UserError(_("You can not create Timesheet Approval Request while type of Approval Type is not Timesheets"))

    @api.constrains('timesheet_line_ids')
    def _check_timesheet_line_ids(self):
        for r in self:
            if len(r.timesheet_line_ids.mapped('employee_id')) > 1:
                raise UserError(_("You can not create Timesheet Approval Request for multiple employees at a time!"))

    def _get_timesheet_domain(self):
        return [
            ('project_id', '!=', False),
            '|', ('approval_id', '=', False), ('approval_id', 'in', self.ids),
            ('timesheet_state', 'in', ('draft', 'confirm')),
            ('employee_id', 'in', self.employee_id.ids),
            # exclude timesheet lines that links to time-off
            ('holiday_id', '=', False),
            ('company_id', 'in', self.company_id.ids)
            ]

    def _load_timesheet_records(self):
        timesheets = self.env['account.analytic.line'].search(self._get_timesheet_domain())
        for r in self:
            r.timesheet_line_ids = [(6, 0, timesheets.filtered(lambda ts: ts.employee_id == r.employee_id).ids)]

    @api.depends('employee_id', 'approval_type_id')
    def _compute_timesheet_lines(self):
        timesheets_request = self.filtered(lambda req: req.approval_type_id.type == 'timesheets')
        timesheets_request._load_timesheet_records()
        (self - timesheets_request).timesheet_line_ids = False

    def _compute_can_validate(self):
        super(ApprovalRequest, self)._compute_can_validate()
        is_timesheet_approver = self.env.user.has_group('hr_timesheet.group_hr_timesheet_approver')
        for r in self.filtered(lambda req: req.approval_type_id.type == 'timesheets'):
            if not is_timesheet_approver:
                r.can_validate = False

    def _compute_can_refuse(self):
        super(ApprovalRequest, self)._compute_can_refuse()
        is_timesheet_approver = self.env.user.has_group('hr_timesheet.group_hr_timesheet_approver')
        for r in self.filtered(lambda req: req.approval_type_id.type == 'timesheets'):
            if not is_timesheet_approver:
                r.can_refuse = False

    @api.depends('timesheet_line_ids.employee_id')
    def _compute_involve_employee_ids(self):
        super(ApprovalRequest, self)._compute_involve_employee_ids()

    def _get_involve_employees(self):
        self.ensure_one()
        # we don't care the self.employee_id as it makes no sense for a timesheet approval request
        if self.type == 'timesheets':
            employees = self.timesheet_line_ids.employee_id
        else:
            employees = super(ApprovalRequest, self)._get_involve_employees()
        return employees

    def action_load_timesheet_records(self):
        self._load_timesheet_records()

    def action_refuse(self):
        if self.type == 'timesheets':
            timesheets = self.timesheet_line_ids.filtered(lambda t: not t.approval_state_exception)
            timesheets.sudo().with_context(ignore_timesheet_approval_state_exception=True).action_refuse()
        return super(ApprovalRequest, self).action_refuse()

    def action_cancel(self):
        if self.type == 'timesheets':
            timesheets = self.timesheet_line_ids.filtered(lambda t: not t.approval_state_exception)
            timesheets.sudo().with_context(ignore_timesheet_approval_state_exception=True).action_cancel()
        return super(ApprovalRequest, self).action_cancel()
