# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class Project(models.Model):
    _inherit = 'project.project'

    def write(self, vals):
        """
            Not allow to archive a project while there is min. a wip timesheet on this project
        """
        for r in self:
            if 'active' in vals and not vals['active'] and any(ts.employee_id and ts.unit_amount == 0.0 for ts in r.timesheet_ids.sudo()):
                raise UserError(_("The project '%s' can only be archived without having any working-in-progress (WIP) timesheet. \n"
                                  "Please end all the WIP timesheets first.") % (r.name))
        return super(Project, self).write(vals)
