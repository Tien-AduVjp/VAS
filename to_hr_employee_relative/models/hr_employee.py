from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    relative_ids = fields.One2many('hr.employee.relative', 'employee_id', string='Related')
    spouse_complete_name = fields.Char(string="Spouse Complete Name", groups="hr.group_hr_user", tracking=True,
                                       compute='_compute_spouse', readonly=False, store=True)
    spouse_birthdate = fields.Date(string="Spouse Birthdate", groups="hr.group_hr_user", tracking=True,
                                   compute='_compute_spouse', readonly=False, store=True)

    @api.depends('relative_ids.type')
    def _compute_marital(self):
        for r in self:
            if any(relative.type in ('wife', 'husband') for relative in r.relative_ids):
                r.marital = 'married'
            else:
                r.marital = r.marital

    @api.depends('relative_ids', 'marital')
    def _compute_spouse(self):
        """If employee has many spouse, spouse_complete_name will is first spouse"""
        for r in self:
            spouse = r.relative_ids.filtered(lambda rel: rel.type in ('wife', 'husband'))[:1]
            if r.marital == 'married':
                if spouse:
                    r.spouse_complete_name = spouse.contact_id.name
                    r.spouse_birthdate = spouse.contact_id.dob
                else:
                    old_relative_spouse = r._origin.relative_ids.filtered(lambda rel: rel.type in ('wife', 'husband'))
                    if old_relative_spouse:
                        r.spouse_complete_name = False
                        r.spouse_birthdate = False
            else:
                r.spouse_complete_name = False
                r.spouse_birthdate = False

    @api.constrains('relative_ids')
    def _check_marital_partner(self):
        for r in self:
            if r.relative_ids and all(type in r.relative_ids.mapped('type') for type in ['wife', 'husband']):
                raise UserError(_("The employee %(name)s can not have both husband and wife at the same time.",
                                  name = r.name
                                  ))
