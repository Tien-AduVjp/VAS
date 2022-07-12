# -*- coding: utf-8 -*-
from odoo import models
from odoo.osv import expression


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    def _get_timesheets_domain(self, date_from, date_to, include_leaves=True):
        domain = super(HrEmployee, self)._get_timesheets_domain(date_from, date_to)
        if not include_leaves:
            leaves = self.env['hr.leave'].sudo().search([
                ('employee_id', 'in', self.ids),
                ('date_from', '<=', date_to),
                ('date_to', '>=', date_from)])
            domain = expression.AND([domain, [('id', 'not in', leaves.mapped('timesheet_ids').ids)]])
        return domain
