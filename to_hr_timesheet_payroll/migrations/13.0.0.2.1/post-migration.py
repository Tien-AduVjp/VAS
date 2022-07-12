# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for payslip in env['hr.payslip'].search([]):
        non_zero_unit_amount_timesheet_entries = payslip.timesheet_line_ids.filtered(lambda l: l.unit_amount != 0.0)
        payslip.write({
            'timesheet_line_ids': [(6, 0, non_zero_unit_amount_timesheet_entries.ids)]
            })

