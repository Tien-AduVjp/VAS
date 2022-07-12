# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'
    
    pow_timesheet_required = fields.Boolean(string='PoW Timesheet Required',
                                             compute='_compute_pow_timesheet_required', store=True, readonly=False, tracking=True,
                                             help="Whether or not Proof-Of-Work timesheet is required. If a time off of this"
                                             " type will be considered as working time (with Unpaid being unchecked, e.g. Work"
                                             " From Home), this field could be checked to require the corresponding time-off"
                                             " employees to record timesheet for proof of work.\n"
                                             "Note: this can be disabled for specific employees with the same option in the main"
                                             " Employee form view.")

    @api.depends('unpaid')
    def _compute_pow_timesheet_required(self):
        for r in self:
            r.pow_timesheet_required = not r.unpaid

    @api.constrains('unpaid', 'pow_timesheet_required')
    def _check_pow_timesheet_required_unpaid(self):
        for r in self:
            if r.pow_timesheet_required and r.unpaid:
                raise UserError(_("PoW Timesheet Required option cannot be enabled for the time-off type"
                                  " '%s' while its Unpaid option is also enabled."))
