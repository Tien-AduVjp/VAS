# -*- coding: utf-8 -*-

from odoo import models, fields


class UserAssignment(models.Model):
    _inherit = 'user.assignment'

    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
