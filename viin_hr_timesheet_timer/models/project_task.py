# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields, models, api, _
from odoo.osv import expression
from odoo.exceptions import UserError


class Task(models.Model):
    _name = 'project.task'
    _inherit = 'project.task'

    timesheet_wip = fields.Boolean(string='Timesheet Log In Progress', compute='_compute_timesheet_wip',
                                   search='_search_timesheet_wip', compute_sudo=True,
                                   help="Technical field to indicate this task has a work in progress timesheet entry")

    start_moment = fields.Datetime('Start moment', compute='_compute_start_moment')
    is_login_user_doing = fields.Boolean('Is login user doing', compute='_compute_login_user_is_doing', compute_sudo=True)

    def _search_timesheet_wip(self, operator, operand):
        all_tasks = self.env['project.task'].search_read([], ['timesheet_wip'])
        if operator == '=':
            if operand:  # equal
                list_ids = [vals['id'] for vals in all_tasks if vals['timesheet_wip'] == operand]
            else:  # is not set, equal = ""
                list_ids = [vals['id'] for vals in all_tasks if not vals['timesheet_wip']]
        elif operator == '!=':
            if operand:
                list_ids = [vals['id'] for vals in all_tasks if vals['timesheet_wip'] != operand]
            else:  # is set
                list_ids = [vals['id'] for vals in all_tasks if vals['timesheet_wip']]
        else:
            return []
        return [('id', 'in', list_ids)]

    def _compute_timesheet_wip(self):
        """
            field 'timesheet_wip' helps to marks whether this task is having any WIP timesheet
            It is primarily used by the 2 filters 'My WIP timesheets' and 'All WIP timesheets'
        """
        timesheet_lines = self.env['account.analytic.line'].sudo().search(self._prepare_employee_timesheet_line_domain())
        for r in self:
            lines = timesheet_lines.filtered(lambda l: l.task_id == r)
            # if this timesheet line is at Working In Progress state
            r.timesheet_wip = any(line.date_start != False and line.date_end == False for line in lines)

    def _compute_login_user_is_doing(self):
        """
            field 'is_login_user_doing' (logging timesheet) helps to determine the invisibility of 2 buttons:
                Log Timesheet
                Stop Log Timesheet
                
            If this value is True:
                >    currently logged in user is logging on this task
                >    'Stop Log Timesheet" will be visible
                >    'Log Timesheet' will be invisible
            Else:
                vice versa.
        """
        timesheet_lines = self.env['account.analytic.line'].search(self._prepare_employee_timesheet_line_domain())
        for r in self:
            lines = timesheet_lines.filtered(lambda l: l.task_id == r)
            # If the current login user is the one who actually starts this timesheet
            r.is_login_user_doing = any(
                line.date_start != False and
                line.date_end == False and
                line.create_uid == self.env.user
                    for line in lines
            )

    @api.depends_context('all_wip_timesheet')
    def _compute_start_moment(self):
        """
            A little trick here:
            start time = real start time - sum of durations of all DONE timesheets (in hours)
            
            Using this trick, we ensures the JS Timer is running correctly including all the time duration
            that this user has been logged in this task.
        """
        for r in self:
            lines = r.timesheet_ids.filtered(
                lambda timesheet: (
                    timesheet.task_id == r and
                    timesheet.date_start and
                    not timesheet.date_end and
                    timesheet.employee_id == self.env.user.employee_id
                )
            ).sorted(
                lambda entry: (entry.date_start, entry.date)
            )
            
            if lines:
                done_timesheet_ids = r.timesheet_ids.filtered(
                    lambda timesheet: (
                        timesheet.employee_id == self.env.user.employee_id and
                        timesheet.unit_amount != 0.0
                    )
                )
                duration = sum(done_timesheet_ids.mapped('unit_amount'))
                r.start_moment = lines[0].date_start - timedelta(hours=duration)
            else:
                r.start_moment = False

    def _prepare_employee_timesheet_line_domain(self):
        """
            The context is sent from the search view 
            when the filter "All WIP timesheets" is activated
            
            Note:
            Task_id domain is used because 
                we are logging timesheet at task level.
                The buttons can only be seen inside a task
        """
        domain = [
            ('employee_id', '!=', False),
            ('project_id', 'in', self.project_id.ids),
            ('task_id', 'in', self.ids),
            ]
        if not self._context.get('all_wip_timesheet', False):
            employee = self._context.get('employee', None) or self.env.user.employee_id
            domain = expression.AND([domain, [('employee_id', '=', employee.id)]])
        return domain

    def _get_wip_timesheet_line_domain(self, employee=None):
        """
            @param employee: if not given, the employee of the current user will be used
        """
        employee = employee or self.env.user.employee_id
        return [
            ('employee_id', '!=', False),
            ('employee_id', '=', employee.id),
            ('project_id', 'in', self.project_id.ids),
            ('task_id', 'in', self.ids),
            ('date_start', '!=', False),
            ('date_end', '=', False),
        ]

    def _check_not_allow_timesheet(self):
        for r in self:
            if not r.allow_timesheets:
                raise UserError(_("You cannot log timesheet on task %s "
                                  "because project %s is configured to not allow to do it. "
                                  "Please edit the project and tick on the 'timesheets' option "
                                  "in order to do timesheet log.")
                                  % (r.name, r.project_id.name)
                                  )

    def write(self, vals):
        """
            Not allow to archive a task while there is min. a wip timesheet on this task
        """
        for r in self:
            if 'active' in vals and not vals['active'] and r.timesheet_wip:
                raise UserError(_("The task '%s' can only be archived without having any working-in-progress (WIP) timesheet. \n"
                                  "Please end all the WIP timesheets first.") % (r.name))
        return super(Task, self).write(vals)
    
    def _check_not_allow_log_multi_timesheet(self):
        for r in self:
            any_wip_timesheet = self.env['account.analytic.line'].sudo().search([
                ('employee_id', '=', self.env.user.employee_id.id),
                ('project_id', '!=', False),
                ('unit_amount', '=', 0.0),
            ], limit=1).sudo() # use sudo to read it's project and task later
            
            # Only check if this timesheet is logged either on active Project or active Task  
            # Ignore if the  project or task is archived
            if any_wip_timesheet.project_id.active and not any_wip_timesheet.task_id:
                raise UserError(_("You cannot log another timesheet "
                                  "while you are currently logging on the project '%s'. "
                                  "Please end the current timesheet logging first.")
                                  % (any_wip_timesheet.project_id.name))
            elif any_wip_timesheet.task_id and any_wip_timesheet.task_id.active:
                raise UserError(_("You cannot log another timesheet "
                                  "while you are currently logging on task '%s' of the project '%s'. "
                                  "Please end the current timesheet logging first.")
                                  % (any_wip_timesheet.task_id.name, any_wip_timesheet.project_id.name))

    def message_unsubscribe(self, partner_ids=None, channel_ids=None):
        employees = self.env['res.users'].search([('partner_id', 'in', partner_ids)]).sudo().employee_id
        for employee in employees:
            self.sudo().with_context(employee=employee).action_stop()
        return super(Task, self).message_unsubscribe(partner_ids, channel_ids)
            
    def action_start(self):
        self._check_not_allow_timesheet()
        for r in self:
            if not r.project_id.active:
                raise UserError(_("It is not allowed to log timesheet on task in an archived project. Please have the project unarchived first."))
            if not r.active:
                raise UserError(_("It is not allowed to log timesheet on an archived task. Please have the task unarchived first."))
            
            r._check_not_allow_log_multi_timesheet()
            last_timesheet_line = self.env['account.analytic.line'].create({
                'date': fields.Date.today(),
                'date_start': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'task_id': r.id,
                'project_id': r.project_id.id,
                'name': r.name or r.project_id.name
                })

    def action_stop(self):
        employee = self._context.get('employee', None)
        for r in self:
            now = fields.Datetime.now()
            for ts_line in r.timesheet_ids.filtered_domain(
                r._get_wip_timesheet_line_domain(employee)
                ).sorted(lambda l: l.time_start):
                if ts_line:
                    if ts_line.date_start.date() == now.date():
                        ts_line.write({
                            'unit_amount': ts_line._get_elapsed_time(),
                        })
                    elif ts_line.date_start.date() <= now.date():
                        raise UserError(_("The start date and end date of the timesheet log must be on the same day for the timesheet recording to be stopped. "
                                          "You cannot stop the process now due to this reason."
                                          "\n\n"
                                          "Please input manually the missing timesheet (start / end) on each corresponding day in order to stop it."
                                        ))
