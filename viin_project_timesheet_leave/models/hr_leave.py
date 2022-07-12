# -*- coding: utf-8 -*-

from odoo import models, fields


class Holidays(models.Model):
    _inherit = 'hr.leave'
    
    timesheet_generate = fields.Boolean(related='holiday_status_id.timesheet_generate',
                                        help="Technical field to improve UI, when kit should show/hide the fields of project and task.")
    project_required = fields.Boolean(related='holiday_status_id.project_required', help="If checked, this time-off requires a project specified.")
    timesheet_project_id = fields.Many2one('project.project', string='Related Project',
                                           help="The project will contain the timesheet generated when this time off is validated."
                                           " Leave empty to use the project specified by the corresponding time-off type.")
    timesheet_task_id = fields.Many2one('project.task', string='Related Task',
                                        domain="[('project_id', '=', timesheet_project_id)]",
                                        help="If this time-off is a project task related one, please specify the task so that"
                                        " we will have Leave time-off registered for the task. Otherwise, leave this empty to use the project specified by the corresponding time-off type.")

    def _timesheet_prepare_line_values(self, index, work_hours_data, day_date, work_hours_count):
        self.ensure_one()
        vals = super(Holidays, self)._timesheet_prepare_line_values(index, work_hours_data, day_date, work_hours_count)
        project = self.timesheet_project_id or self.holiday_status_id.timesheet_project_id

        if self.timesheet_project_id:
            if self.timesheet_project_id == self.holiday_status_id.timesheet_project_id:
                task = self.timesheet_task_id or self.holiday_status_id.timesheet_task_id
            else:
                task = self.timesheet_task_id
        else:
            task = self.holiday_status_id.timesheet_task_id

        vals.update({
            'project_id': project and project.id or False,
            'task_id': task and task.id or False
            })
        return vals
