from odoo import models, fields, api


class HrJob(models.Model):
    _inherit = 'hr.job'

    skill_description_ids = fields.Many2many('hr.skill.description', 'hr_job_skill_description_required_rel', 'job_id', 'skill_description_id',
                                             compute='_compute_skill_description_ids', store=True,
                                             string='Required Skills',
                                             help="The skills that the employees of this job position are required to have.")
    preferred_skill_description_ids = fields.Many2many('hr.skill.description', 'hr_job_skill_description_preferred_rel', 'job_id', 'skill_description_id',
                                                       compute='_compute_preferred_skill_description_ids', store=True,
                                                       string='Preferred Skills',
                                                       help="The skills that the employees of this job position are preferred to have.")

    @api.depends('rank_ids.skill_description_ids')
    def _compute_skill_description_ids(self):
        for r in self:
            r.skill_description_ids = r.rank_ids.skill_description_ids

    @api.depends('rank_ids.preferred_skill_description_ids')
    def _compute_preferred_skill_description_ids(self):
        for r in self:
            r.preferred_skill_description_ids = r.rank_ids.preferred_skill_description_ids
