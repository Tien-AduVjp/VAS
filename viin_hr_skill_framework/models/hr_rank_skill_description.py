from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SkillRequirement(models.Model):
    _name = 'hr.rank.skill.description'
    _inherit = ['hr.skill.description.abstract']
    _description = 'Rank Skill Description Line'

    name = fields.Char(string='Name', compute='_compute_name', translate=True)
    rank_id = fields.Many2one('hr.rank', string='Rank', required=True, ondelete='cascade', tracking=True)
    expectation = fields.Selection([
        ('required', 'Required'),
        ('preferred', 'Preferred')], default='required', required=True, string='Expectation', tracking=True)
    skill_description_id = fields.Many2one('hr.skill.description', compute='_compute_skill_description_id', store=True, tracking=True)
    description = fields.Html(related='skill_description_id.description', translate=True, readonly=False)

    _sql_constraints = [
        ('combination_unique',
         'UNIQUE(skill_type_id, skill_id, skill_level_id, rank_id)',
         "Overlapped skills of the same level is not allowed!"),
        ('combination_expectation_unique',
         'UNIQUE(skill_type_id, skill_id, expectation, rank_id)',
         "Overlapped skills of the same expectation is not allowed!"),
    ]

    @api.depends('skill_type_id', 'skill_id', 'skill_level_id')
    def _compute_skill_description_id(self):
        skill_descriptions = self._lookup_skill_description()
        for r in self:
            r.skill_description_id = skill_descriptions.filtered(
                lambda rec: \
                rec.skill_type_id == r.skill_type_id \
                and rec.skill_id == r.skill_id \
                and rec.skill_level_id == r.skill_level_id
                )[:1]

    @api.constrains('rank_id', 'skill_type_id', 'skill_id', 'expectation')
    def _check_level_expectation(self):
        for r in self:
            same_skill_records = self.env['hr.rank.skill.description'].search([
                ('id', '!=', r.id),
                ('rank_id', '=', r.rank_id.id),
                ('skill_type_id', '=', r.skill_type_id.id),
                ('skill_id', '=', r.skill_id.id),
                ('expectation', '!=', r.expectation)
                ])
            if r.expectation == 'preferred' and any(
                rec.expectation == 'required' \
                and rec.skill_level_id.level_progress >= r.skill_level_id.level_progress \
                for rec in same_skill_records
                ):
                raise UserError(_("Preferred skills should be at higher skill level than required skills"))
            if r.expectation == 'required' and any(
                rec.expectation == 'preferred' \
                and rec.skill_level_id.level_progress <= r.skill_level_id.level_progress \
                for rec in same_skill_records
                ):
                raise UserError(_("Required skills should be at lower skill level than preferred skills"))
            
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        records = super(SkillRequirement, self).create(vals_list)
        records.filtered(lambda r: not r.skill_description_id)._generate_description_record_if_not_exists()
        return records

    def write(self, vals):
        res = super(SkillRequirement, self).write(vals)
        self.filtered(lambda r: not r.skill_description_id)._generate_description_record_if_not_exists()
        return res

    def _prepare_lookup_skill_description_domain(self):
        return [
            '|', '|',
            ('skill_type_id', 'in', self.skill_type_id.ids),
            ('skill_id', 'in', self.skill_id.ids),
            ('skill_level_id', 'in', self.skill_level_id.ids)
            ]

    def _lookup_skill_description(self):
        return self.env['hr.skill.description'].search(self._prepare_lookup_skill_description_domain())

    def _prepare_skill_desc_vals(self):
        self.ensure_one()
        return {
            'skill_type_id': self.skill_type_id.id,
            'skill_id': self.skill_id.id,
            'skill_level_id': self.skill_level_id.id,
            'description': self.description
            }

    def _generate_description_record_if_not_exists(self):
        for r in self:
            desc = r._lookup_skill_description()
            if not desc:
                desc = self.env['hr.skill.description'].create(r._prepare_skill_desc_vals())
            r.skill_description_id = desc[:1]

    def _consolidate(self):
        """This consolidates skill descriptions in self to avoid duplication"""
        consolidated_records = self.env['hr.rank.skill.description']
        for r in self:
            candidates = self.filtered(
                lambda rec: rec.skill_type_id.id == r.skill_type_id.id \
                and rec.skill_id.id == r.skill_id.id
                )
            selected = candidates[:1]
            for candidate in candidates[1:]:
                if selected.expectation == 'required':
                    if candidate.skill_level_id.level_progress >= selected.skill_level_id.level_progress and candidate.expectation == 'required':
                        selected = candidate
                else:
                    if candidate.expectation == 'required':
                        if candidate.skill_level_id.level_progress < selected.skill_level_id.level_progress:
                            consolidated_records |= selected
                        selected = candidate
            consolidated_records |= selected
        # ensure required skills come first
        consolidated_records = consolidated_records.sorted(
            lambda rec: (rec.expectation == 'required', rec.expectation == 'preferred'),
            reverse=True
            )
        return consolidated_records
