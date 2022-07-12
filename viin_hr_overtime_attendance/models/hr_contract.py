# -*- coding: utf-8 -*-

from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    overtime_recognition_mode = fields.Selection(selection_add=[('attendance', 'Attendance')], ondelete={'attendance':'set default'})

