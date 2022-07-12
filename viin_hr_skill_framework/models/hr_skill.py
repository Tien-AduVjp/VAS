# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Skill(models.Model):
    _inherit = 'hr.skill'

    # begin override
    name = fields.Char(translate=True)
    # end override
    code = fields.Char(string='Code', help="Code of the skill. You may look up SFIA for reference / examples.")
    description = fields.Text(string='Description', translate=True,
                              help="A short description of the skill")
    skill_level_ids = fields.Many2many('hr.skill.level', 'hr_skill_hr_skill_level_rel', 'skill_id', 'skill_level_id',
                                       string='Skill Levels',
                                       compute='_compute_skill_level_ids', store=True,
                                       help="Skill levels related to this skill.")

    @api.depends('skill_type_id.skill_level_ids')
    def _compute_skill_level_ids(self):
        for r in self:
            r.skill_level_ids = r.skill_type_id.skill_level_ids
