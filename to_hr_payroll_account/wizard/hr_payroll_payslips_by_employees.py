# -*- coding: utf-8 -*-

from odoo import api, models


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def compute_sheet(self):
        journal = self.batch_id.journal_id or self.env['hr.payslip.run']._get_default_journal_id()
        return super(HrPayslipEmployees, self.with_context(journal_id=journal.id)).compute_sheet()
