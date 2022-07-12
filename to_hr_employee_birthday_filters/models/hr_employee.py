# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Employee(models.Model):
    _inherit = 'hr.employee'

    birthday = fields.Date(compute='_get_birthday', inverse='_set_birthday', store=True, groups='hr.group_hr_user')
    dyob = fields.Integer(string='Day of Birth', compute='_compute_yy_mm_of_birth', store=True, groups='hr.group_hr_user')
    mob = fields.Integer(string='Month of Birth', compute='_compute_yy_mm_of_birth', store=True, groups='hr.group_hr_user')
    yob = fields.Integer(string='Year of Birth', compute='_compute_yy_mm_of_birth', store=True, groups='hr.group_hr_user')
    birthday_by_week = fields.Selection([
        ('this_week', 'This week'),
        ('last_week', 'Last week'),
        ('next_week', 'Next week')],
        search='_search_birthday', store=False, help="Technical field, use to filter")

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

    def _search_birthday(self, operator, value):
        domain = []
        date = fields.Date.today()
        # get the first day of the week and the last day of the week
        date_from = fields.Date.start_of(date, 'week')
        date_to = fields.Date.end_of(date, 'week')
        month_start = fields.Date.start_of(date_from,'month')
        month_end = fields.Date.end_of(date_to,'month')
        if value == 'next_week':
            #get the first day of the week next and the last day of the week next
            date_from = fields.Date.add(date_to, days=1)
            date_to = fields.Date.end_of(date_from, 'week')
        if value == 'last_week':
            # get the first day of the week last and the last day of the week last
            date_to = fields.Date.add(date_from, days=-1)
            date_from = fields.Date.start_of(date_to, 'week')
        if operator == '=' and not value:
            domain = [('birthday', '=', False)]
        if operator == '!=' and not value:
            domain = [('birthday', '!=', False)]
        if operator == '=' and value:
            if date_from.month == date_to.month:
                domain = [ ('dyob', '>=', date_from.day),
                          ('dyob', '<=', date_to.day),
                          ('mob', '=', date_from.month)]
            else:
                domain = ['|',
                            '&', ('dyob', '>=', date_from.day), ('mob', '=', date_from.month),
                            '&', ('dyob', '<=', date_to.day), ('mob', '=', date_to.month)]
        if operator == '!=' and value:
            if date_from.month == date_to.month:
                domain = ['|',
                            '&', ('mob', '!=', date_from.month), ('birthday', '!=', False),
                            '&', ('mob', '=', date_from.month),
                            '|', ('dyob', '<', date_from.day),
                                 ('dyob', '>', date_to.day),]
            else:
                domain = ['|', '|',
                            '&', '&', ('mob', '!=', date_from.month), ('mob', '!=', date_to.month), ('birthday', '!=', False),
                            '&', '&', ('dyob', '<', date_from.day), ('dyob', '>', month_start.day), ('mob', '=', date_from.month),
                            '&', '&', ('dyob', '>', date_to.day), ('dyob', '<', month_end.day), ('mob', '=', date_to.month)]
        return domain
