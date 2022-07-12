# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class TimesheetApprovalRequestCreate(models.TransientModel):
    _name = "timesheet.approval.request.create"
    _description = "Create Timesheet Approval Request for Timesheet lines"

    @api.model
    def default_get(self, fields_list):
        res = super(TimesheetApprovalRequestCreate, self).default_get(fields_list)
        if self._context.get('active_model') == 'account.analytic.line':
            timesheet_lines = self.env['account.analytic.line'].browse(self._context.get('active_ids')).sudo()
            res['timesheet_line_ids'] = [(6, 0, timesheet_lines.ids)]
            res['employee_id'] = timesheet_lines.employee_id[:1].id
            res['company_id'] = timesheet_lines.company_id[:1].id
        
        timesheet_type = self.env['approval.request.type'].search([
            ('type', '=', 'timesheets'),
            ('company_id', '=', res.get('company_id', self.env.company.id))
            ], limit=1)
        res['approval_type_id'] = timesheet_type.id
        return res

    title = fields.Char(string='Title', required=True)
    timesheet_line_ids = fields.Many2many('account.analytic.line', string='Timesheet Records')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    company_id = fields.Many2one('res.company', string='Company')
    approval_type_id = fields.Many2one('approval.request.type', string='Request Type')

    @api.constrains('timesheet_line_ids')
    def _check_timesheet_line_ids(self):
        for r in self:
            timesheet_line_ids = r.timesheet_line_ids
            line_not_draft = timesheet_line_ids.filtered(lambda x: x.timesheet_state != 'draft')
            if line_not_draft:
                raise UserError(_("You can not create Timesheet Approval Request while timesheet line is not Draft state!"
                                  "\nDate: %s \nDescription: %s, \nState: %s")
                                  % (
                                      line_not_draft[0].date, line_not_draft[0].name, \
                                      dict(
                                          timesheet_line_ids._fields['timesheet_state'].selection
                                          ).get(line_not_draft[0].timesheet_state)
                                    )
                                  )
            employee_ids = timesheet_line_ids.mapped('employee_id')
            if employee_ids and len(employee_ids) > 1:
                raise UserError(_("You can not create Timesheet Approval Request for multiple employees !"))
            if timesheet_line_ids.mapped('approval_id'):
                raise UserError(_("You can not create Timesheet Approval Request when timesheet line has approval request !"))
            if employee_ids != self.env.user.employee_id:
                child_of_user = self.env['hr.employee'].sudo().search([('id', 'child_of', self.env.user.employee_id.id)])
                if employee_ids not in child_of_user:
                    raise UserError(_("You can not create Timesheet Approval Request for employees who are not your subordinates !"))

    def _prepare_approval_request_vals(self):
        self.ensure_one()
        self = self.sudo()
        return {
            'title': self.title,
            'employee_id': self.env.user.employee_id.id or self.employee_id.id,
            'timesheet_line_ids': [(6, 0, self.timesheet_line_ids.ids)],
            'approval_type_id': self.approval_type_id.id,
            'date': fields.Date.today(),
            'company_id': self.company_id.id,
            }

    def action_create_timesheet_approval_request(self):
        self.ensure_one()
        approval = self.env['approval.request'].create(self._prepare_approval_request_vals())
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Timesheet Approval Request',
            'res_model': 'approval.request',
            'res_id': approval.id,
            'view_mode': 'form',
            'target':'current'
            }
        return action
