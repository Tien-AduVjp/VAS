# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.tools import relativedelta
from odoo.exceptions import UserError

from odoo.addons.to_approvals.models.abstract_approval_request_line import STATUS


class AccountAnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _inherit = ['account.analytic.line', 'abstract.approval.request.line', 'mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'
    
    #-------------BEGIN: override------------#
    name = fields.Char(tracking=True)
    account_id = fields.Many2one(tracking=True)
    amount = fields.Monetary(tracking=True)
    unit_amount = fields.Float(tracking=True)
    #-------------END: override------------#

    timesheet_state = fields.Selection(STATUS, string='Timesheet State', tracking=True, copy=False, default='draft')

    approval_id = fields.Many2one('approval.request', string="Approval Request", tracking=True,
                                  help="The related approval request of this timesheet record.")
    parent_state = fields.Selection(related='approval_id.state', store=True)
    
    def _get_state_field(self):
        return 'timesheet_state'

    @api.constrains('approval_id', 'project_id')
    def _check_is_valid_for_approval(self):
        for r in self:
            if r.approval_id and not r.project_id:
                raise UserError(_("You can not add a timesheet record that does not have a project specified for timesheet approval."))

    @api.constrains('employee_id', 'approval_id')
    def _check_employee_id(self):
        self.approval_id._check_employee()

    @api.model
    def _test_timesheet(self, vals):
        # TODO: remove me in master/14+
        return vals.get('project_id', False) and vals.get('employee_id', False) and not vals.get('holiday_id', False)
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override to force approved for lines that do not require approval
        """
        records = super(AccountAnalyticLine, self).create(vals_list)
        records._auto_approve()
        return records
    
    @api.model
    def _get_write_projected_fields(self):
        return [
            'project_id',
            'employee_id',
            'task_id',
            'amount',
            'unit_amount'
            ]
    
    def write(self, vals):
        """
        Override to avoid modifying timesheets that already approved/validated
        """
        timesheets_before_save = self.filtered(lambda l: l.employee_id and l.project_id and not l.holiday_id)
        if any(field in vals for field in self._get_write_projected_fields()) and not self.env.user.has_group('hr_timesheet.group_timesheet_manager'):
            for r in timesheets_before_save:
                if r.approval_id and r.timesheet_state in ('validate1', 'validate'):
                    raise UserError(_("You are not allowed to modify the timesheet record '%s' which is either"
                                          " under approval process or already approved. Please ask your manager or"
                                          " someone who is granted with '%s' access rights for help.")
                                          % (r.display_name, self.env.ref('hr_timesheet.group_timesheet_manager').display_name))
        return super(AccountAnalyticLine, self).write(vals)

    def _auto_approve(self):
        """
        records in self will be auto approved if they are not timesheet entries or approval is not required
        """
        auto_approve = self.filtered(lambda l: (not l.employee_id or not l.project_id or l.holiday_id) and l.timesheet_state != 'validate')
        to_approve_timesheet_lines = (self - auto_approve).filtered(
            lambda r: r.employee_id \
            and r.project_id \
            and not r.holiday_id \
            and r.timesheet_state != 'validate'
            ).sorted('date')
        if to_approve_timesheet_lines:
            employees = to_approve_timesheet_lines.with_context(active_test=False).employee_id
            related_contracts = employees.sudo()._get_contracts(
                to_approve_timesheet_lines[0].date,
                to_approve_timesheet_lines[-1].date,
                states=['open', 'close'])
            for employee in employees:
                for contract in related_contracts.filtered(lambda c: c.employee_id == employee and not c.timesheet_approval):
                    contract_date_end = contract.date_end or contract.trial_date_end or fields.Date.today() + relativedelta(years=1000)
                    auto_approve |= to_approve_timesheet_lines.filtered(
                        lambda l: l.employee_id == employee \
                        and l.date >= contract.date_start
                        and l.date <= contract_date_end
                        )
        if auto_approve:
            auto_approve.write({
                'timesheet_state':'validate'
                })
        return auto_approve
