from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrRank(models.Model):
    _inherit = 'hr.rank'
    
    rank_skill_description_ids = fields.One2many('hr.rank.skill.description', 'rank_id', string='Skill Requirements')
    child_rank_skill_description_ids = fields.Many2many('hr.rank.skill.description', 'hr_rank_child_hr_rank_skill_description_rel',
                                                        'rank_id', 'rank_skill_description_id',
                                                        compute='_compute_child_rank_skill_description_ids', store=False,
                                                        string='Child Rank Skill Descriptions')
    consolidated_rank_skill_description_ids = fields.Many2many('hr.rank.skill.description', 'hr_rank_hr_rank_skill_description_rel',
                                                               'rank_id', 'rank_skill_description_id',
                                                               compute='_compute_consolidated_rank_skill_description_ids', store=True,
                                                               string='Consolidated Rank Skill Descriptions',
                                                               help="Skill description records that are consolidated from the child records and current records")
    skill_description_ids = fields.Many2many('hr.skill.description', 'hr_rank_skill_description_required_rel',
                                             'rank_id', 'skill_description_id',
                                             compute='_compute_skill_description_ids', store=True,
                                             string='Required Skills')
    skill_descriptions_count = fields.Integer(string='Required Skills Count', compute='_compute_skill_descriptions_count')
    preferred_skill_description_ids = fields.Many2many('hr.skill.description', 'hr_rank_skill_description_preferred_rel',
                                             'rank_id', 'skill_description_id',
                                             compute='_compute_preferred_skill_description_ids', store=True,
                                             string='Preferred Skills',
                                             help="The skills that the employees of this rank are preferred to have.")
    preferred_skill_descriptions_count = fields.Integer(string='Preferred Skills Count', compute='_compute_preferred_skill_descriptions_count')
    to_qualify_employee_ids = fields.One2many('hr.employee', 'rank_id', string='To-Qualify Employees',
                                              domain="[('unmet_skill_report_ids','!=',False)]",
                                              help="The employees are currently set at this rank but have some unmet skills")
    to_qualify_employees_count = fields.Integer(string='To-Qualify Employees Count', compute='_compute_to_qualify_employees_count', compute_sudo=True)

    @api.depends('recursive_child_ids.rank_skill_description_ids')
    def _compute_child_rank_skill_description_ids(self):
        for r in self:
            r.child_rank_skill_description_ids = r.recursive_child_ids.rank_skill_description_ids._consolidate()

    @api.depends('rank_skill_description_ids', 'recursive_child_ids.rank_skill_description_ids')
    def _compute_consolidated_rank_skill_description_ids(self):
        for r in self:
            r.consolidated_rank_skill_description_ids = (
                r.rank_skill_description_ids | r.recursive_child_ids.rank_skill_description_ids
                )._consolidate()

    @api.depends(
        'consolidated_rank_skill_description_ids.expectation',
        'consolidated_rank_skill_description_ids.skill_description_id')
    def _compute_skill_description_ids(self):
        for r in self:
            r.skill_description_ids = r.consolidated_rank_skill_description_ids.filtered(
                lambda rec: rec.expectation == 'required'
                ).skill_description_id

    @api.depends('skill_description_ids')
    def _compute_skill_descriptions_count(self):
        for r in self:
            r.skill_descriptions_count = len(r.skill_description_ids)

    @api.depends(
        'consolidated_rank_skill_description_ids.expectation',
        'consolidated_rank_skill_description_ids.skill_description_id')
    def _compute_preferred_skill_description_ids(self):
        for r in self:
            r.preferred_skill_description_ids = r.consolidated_rank_skill_description_ids.filtered(
                lambda rec: rec.expectation == 'preferred'
                ).skill_description_id

    @api.depends('preferred_skill_description_ids')
    def _compute_preferred_skill_descriptions_count(self):
        for r in self:
            r.preferred_skill_descriptions_count = len(r.preferred_skill_description_ids)

    def _compute_to_qualify_employees_count(self):
        employees_data = self.env['hr.employee'].read_group([
            ('rank_id', 'in', self.ids),
            ('unmet_skill_report_ids', '!=', False),
            ], ['rank_id'], ['rank_id'])
        mapped_data = dict([(dict_data['rank_id'][0], dict_data['rank_id_count']) for dict_data in employees_data])
        for r in self:
            r.to_qualify_employees_count = mapped_data.get(r.id, 0)

    def action_view_required_skill_descriptions(self):
        action = self.env.ref('viin_hr_skill_framework.action_skill_description')
        result = action.read()[0]
        result['context'] = {
            'default_department_id': self[:1].id,
            }
        result['domain'] = "[('id','in',%s)]" % self.skill_description_ids.ids
        return result

    def action_view_preferred_skill_descriptions(self):
        action = self.env.ref('viin_hr_skill_framework.action_skill_description')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('id','in',%s)]" % self.preferred_skill_description_ids.ids
        return result
