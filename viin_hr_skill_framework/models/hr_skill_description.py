from odoo import models, fields, api


class HrSkillDescription(models.Model):
    _name = 'hr.skill.description'
    _inherit = ['hr.skill.description.abstract']
    _description = "Skill Description"

    skill_type_id = fields.Many2one(readonly=True)
    skill_id = fields.Many2one(readonly=True)
    skill_level_id = fields.Many2one(readonly=True)
    required_by_rank_ids = fields.Many2many('hr.rank', 'hr_rank_skill_description_required_rel', 'skill_description_id', 'rank_id',
                                            string='Required by Ranks', readonly=True,
                                            help="The ranks that require this skill.")
    preferred_by_rank_ids = fields.Many2many('hr.rank', 'hr_rank_skill_description_preferred_rel', 'skill_description_id', 'rank_id',
                                            string='Preferred by Ranks', readonly=True,
                                            help="The ranks that require this skill as optional (not mandatory).")

    _sql_constraints = [
        ('combination_unique',
         'UNIQUE(skill_type_id, skill_id, skill_level_id)',
         "There must not be more than one skill description record of the same Skill Type and Skill and Skill Level!"),
    ]
