# -*- coding: utf-8 -*-

from odoo import fields, models, api


class HolidaysType(models.Model):
    _inherit = 'hr.leave.type'

    project_required = fields.Boolean(string='Project Required',
                                      compute='_compute_project_required',
                                      store=True,
                                      readonly=False,
                                      help="If checked, all the time-off of this type will require a project specified."
                                      " Otherwise, inputing project on time-off is just optional.")
    time_type = fields.Selection(compute='_compute_time_type', store=True)

    @api.depends('timesheet_generate')
    def _compute_project_required(self):
        for r in self:
            if not r.timesheet_generate:
                r.project_required = False
            else:
                r.project_required = r.project_required

    @api.depends('project_required')
    def _compute_time_type(self):
        for r in self:
            r.time_type = 'other' if r.project_required else 'leave'
