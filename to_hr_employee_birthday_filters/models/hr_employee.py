# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    birthday = fields.Date(compute='_get_birthday', inverse='_set_birthday', store=True, groups='hr.group_hr_user')
    dyob = fields.Integer(string='Day of Birth', compute='_compute_yy_mm_of_birth', store=True, groups='hr.group_hr_user')
    mob = fields.Integer(string='Month of Birth', compute='_compute_yy_mm_of_birth', store=True, groups='hr.group_hr_user')
    yob = fields.Integer(string='Year of Birth', compute='_compute_yy_mm_of_birth', store=True, groups='hr.group_hr_user')

    @api.depends('address_home_id.dob')
    def _get_birthday(self):
        for r in self:
            if not r.birthday or r.address_home_id.dob:
                r.birthday = r.address_home_id.dob
    
    def _set_birthday(self):
        for r in self:
            if r.address_home_id and r.birthday and r.birthday != r.address_home_id.dob:
                r.address_home_id.write({'dob': r.birthday})

    @api.depends('birthday')
    def _compute_yy_mm_of_birth(self):
        for r in self:
            if not r.birthday:
                r.mob = False
                r.yob = False
                r.dyob = False
            else:
                year, month, day = self.env['to.base'].split_date(r.birthday)
                r.dyob = day
                r.mob = month
                r.yob = year
