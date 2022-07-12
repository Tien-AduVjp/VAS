from odoo import api, fields, models


class EmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'
    
    skill_description_id = fields.Many2one('hr.skill.description',
                                           string='Skill Description Entry',
                                           compute='_compute_skill_description_id')
    skill_description = fields.Html(string='Skill Description',
                                    compute='_compute_skill_description_id')

    @api.depends('skill_type_id', 'skill_id', 'skill_level_id')
    def _compute_skill_description_id(self):
        for r in self:
            r.skill_description_id = r.skill_type_id.hr_skill_description_ids.filtered(
                lambda sd: sd.skill_id == r.skill_id 
                and sd.skill_level_id == r.skill_level_id)[:1]
            r.skill_description = r.skill_description_id.description
