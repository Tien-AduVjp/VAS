from odoo import models, fields, api


class AbstractHrSkillDescription(models.AbstractModel):
    _name = 'hr.skill.description.abstract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Skill Description Abstract"

    name = fields.Char(string='Title', compute='_compute_name', translate=True)
    skill_type_id = fields.Many2one('hr.skill.type', string='Skill Type', required=True, ondelete='cascade', tracking=True)
    skill_id = fields.Many2one('hr.skill', string='Skill', required=True, ondelete='cascade', tracking=True,
                               domain="[('skill_type_id','=',skill_type_id)]")
    skill_level_id = fields.Many2one('hr.skill.level', string='Skill Level', required=True, ondelete='cascade',
                                     domain="[('skill_type_id','=',skill_type_id)]", tracking=True)
    level_progress = fields.Integer(related='skill_level_id.level_progress')
    description = fields.Html(string='Descriptions', translate=True)

    @api.depends('skill_type_id.name', 'skill_id.name', 'skill_level_id.name')
    def _compute_name(self):
        for r in self:
            r.name = "[%s] %s - %s" % (r.skill_type_id.name, r.skill_id.name, r.skill_level_id.name)

    @api.onchange('skill_type_id')
    def _onchange_skill(self):
        """
        This is for form views only. Do NOT convert it to compute
        """
        skills = self.env['hr.skill'].search([('skill_type_id', 'in', self.skill_type_id.ids)])
        skill_levels = self.env['hr.skill.level'].search([('skill_type_id', 'in', self.skill_type_id.ids)])
        for r in self:
            r.skill_id = skills.filtered(lambda sk: sk.skill_type_id == r.skill_type_id)[:1]
            r.skill_level_id = skill_levels.filtered(lambda l: l.skill_type_id == r.skill_type_id)[:1]
