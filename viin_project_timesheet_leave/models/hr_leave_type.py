# -*- coding: utf-8 -*-

from odoo import fields, models, api


class HolidaysType(models.Model):
    _inherit = 'hr.leave.type'

    project_required = fields.Boolean(string='Project Required',
                                      help="If checked, all the time-off of this type will require a project specified."
                                      " Otherwise, inputing project on time-off is just optional.")
    
    @api.onchange('timesheet_generate')
    def _onchange_timesheet_generate(self):
        if not self.timesheet_generate:
            self.project_required = False
            
    @api.onchange('project_required')
    def _onchange_project_required(self):
        if self.project_required:
            self.time_type = 'other'
        else:
            self.time_type = 'leave'
