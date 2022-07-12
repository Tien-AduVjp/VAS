# -*- coding: utf-8 -*-

from datetime import datetime, date, time

from odoo import models, api


class HrContract(models.Model):
    _inherit = "hr.contract"

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        contracts = super(HrContract, self).create(vals_list)
        contracts_to_trigger = contracts.filtered(lambda c: c.state in ['open', 'close'])
        hr_attendances = contracts_to_trigger._get_affected_hr_attendance()
        if hr_attendances:
            hr_attendances.sudo()._compute_valid_check_in_check_out()
        return contracts

    def write(self, vals):
        hr_attendances = self.env['hr.attendance'].sudo()
        recompute = any(f in vals for f in self._get_fields_to_trigger_recompute_hr_attendance())
        if recompute:
            hr_attendances |= self._get_affected_hr_attendance()
        res = super(HrContract, self).write(vals)
        if recompute:
            hr_attendances |= self._get_affected_hr_attendance()
        if hr_attendances:
            hr_attendances.sudo()._compute_valid_check_in_check_out()
        return res

    def unlink(self):
        hr_attendances = self._get_affected_hr_attendance()
        res = super(HrContract, self).unlink()
        if hr_attendances:
            hr_attendances.sudo()._compute_valid_check_in_check_out()
        return res

    def _get_fields_to_trigger_recompute_hr_attendance(self):
        return ['date_start', 'date_end', 'state', 'employee_id', 'resource_calendar_id']

    def _get_affected_hr_attendance(self):
        return self.env['hr.attendance'].sudo().search(self._prepare_affected_hr_attendance_domain())

    def _prepare_affected_hr_attendance_domain(self):
        self = self.filtered(lambda c: c.state in ['open', 'close']).sorted('date_start')
        return [
            ('employee_id', 'in', self.employee_id.ids),
            ('check_in', '<=', datetime.combine(self[-1:].date_end or date(9999, 12, 31), time.max)),
            ('check_out', '>=', datetime.combine(self[:1].date_start or date(9999, 12, 31), time.min)),
            ]
