from odoo import models, fields, api, registry


class ResPartner(models.Model):
    _inherit = 'res.partner'

    dob = fields.Date(string='Birth Day', index=True)
    date_of_establishment = fields.Date(string='Date of Establishment', related='dob', readonly=False)
    dyob = fields.Integer("Day of Birth", compute='_compute_yy_mm_of_birth', store=True, index=True,
                         help="The technical field storing the partner's day of birth which is calculated based on the Date of Birth.")
    mob = fields.Integer(string='Month of Birth', compute='_compute_yy_mm_of_birth', store=True, index=True,
                         help="The technical field storing the partner's month of birth which is calculated based on the Date of Birth.")
    yob = fields.Integer(string='Year of Birth', compute='_compute_yy_mm_of_birth', store=True, index=True,
                         help="The technical field storing the partner's year of birth which is calculated based on the Date of Birth.")

    @api.depends('dob')
    def _compute_yy_mm_of_birth(self):
        for r in self:
            if not r.dob:
                r.mob = False
                r.yob = False
                r.dyob = False
            else:
                year, month, day = self.env['to.base'].split_date(r.dob)
                r.dyob = day
                r.mob = month
                r.yob = year
