# -*- coding: utf-8 -*-

from odoo import models, api


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        leaves = super(ResourceCalendarLeaves, self).create(vals_list)
        hr_attendances = leaves._get_affected_hr_attendance()
        if hr_attendances:
            hr_attendances.sudo()._compute_valid_check_in_check_out()
        return leaves

    def write(self, vals):
        hr_attendances = self.env['hr.attendance'].sudo()
        recompute = any(f in vals for f in self._get_fields_to_trigger_recompute_hr_attendance())
        if recompute:
            hr_attendances |= self._get_affected_hr_attendance()
        res = super(ResourceCalendarLeaves, self).write(vals)
        if recompute:
            hr_attendances |= self._get_affected_hr_attendance()
        if hr_attendances:
            hr_attendances.sudo()._compute_valid_check_in_check_out()
        return res

    def unlink(self):
        hr_attendances = self._get_affected_hr_attendance()
        res = super(ResourceCalendarLeaves, self).unlink()
        if hr_attendances:
            hr_attendances.sudo()._compute_valid_check_in_check_out()
        return res

    def _get_fields_to_trigger_recompute_hr_attendance(self):
        return ['calendar_id', 'resource_id', 'date_from', 'date_to', 'time_type']

    def _get_affected_hr_attendance(self):
        return self.env['hr.attendance'].sudo().search(self._prepare_affected_hr_attendance_domain())

    def _prepare_affected_hr_attendance_domain(self):
        self = self.sorted('date_from')
        return [
            ('check_in', '<=', self[-1:].date_to),
            ('check_out', '>=', self[:1].date_from),
            ]
