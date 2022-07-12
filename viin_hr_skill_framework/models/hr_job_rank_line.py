from odoo import models, fields, api


class HrJobRankLine(models.Model):
    _inherit = 'hr.job.rank.line'

    skill_description_ids = fields.Many2many('hr.skill.description', compute='_compute_skill_description_ids',
                                             string='Required Skills')
    preferred_skill_description_ids = fields.Many2many('hr.skill.description', compute='_compute_preferred_skill_description_ids',
                                                       string='Preferred Skills')

    @api.depends('rank_id.skill_description_ids')
    def _compute_skill_description_ids(self):
        for r in self:
            r.skill_description_ids = r.rank_id.skill_description_ids

    @api.depends('rank_id.preferred_skill_description_ids')
    def _compute_preferred_skill_description_ids(self):
        for r in self:
            r.preferred_skill_description_ids = r.rank_id.preferred_skill_description_ids
