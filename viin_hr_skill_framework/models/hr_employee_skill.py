from odoo import api, fields, models,_


class EmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'

    skill_description = fields.Html(string='Skill Description',
                                    compute='_compute_skill_description')

    @api.depends('skill_type_id', 'skill_id', 'skill_level_id')
    def _compute_skill_description(self):
        for r in self:
            r.skill_description = r.skill_type_id.hr_skill_description_ids.filtered(
                lambda sd: sd.skill_id == r.skill_id
                and sd.skill_level_id == r.skill_level_id)[:1].description
            if not r.skill_description:
                r.skill_description = _("This skill does not have any description. Please update the description for this skill.")
