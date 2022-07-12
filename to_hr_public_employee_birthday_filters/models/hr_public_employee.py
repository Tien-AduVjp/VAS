from odoo import api, fields, models


class HrPublicEmployee(models.Model):
    _inherit = 'hr.employee.public'
    
    birthday = fields.Date(string='Date of Birth', compute='_get_birthday', inverse='_set_birthday', store=True)
    dyob = fields.Integer(string='Day of Birth', compute='_compute_yy_mm_of_birth', store=True)
    mob = fields.Integer(string='Month of Birth', compute='_compute_yy_mm_of_birth', store=True)
    yob = fields.Integer(string='Year of Birth', compute='_compute_yy_mm_of_birth', store=True)
    
    @api.depends('address_id.dob')
    def _get_birthday(self):
        for r in self:
            birthday = r.birthday
            if not birthday and r.address_id.dob:
                r.birthday = r.address_id.dob
            else:
                r.birthday = birthday
    
    def _set_birthday(self):
        for r in self:
            if r.address_id and r.birthday and r.birthday != r.address_id.dob:
                r.address_id.write({'dob': r.birthday})
    
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
