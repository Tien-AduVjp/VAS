from odoo import models, fields, api


class SkillRequirement(models.Model):
    _name = 'hr.skill.type'
    _inherit = ['mail.thread', 'hr.skill.type', 'mail.activity.mixin']

    # begin override
    name = fields.Char(translate=True)
    # end override

    hr_skill_description_ids = fields.One2many('hr.skill.description', 'skill_type_id', string='Description Entries')
    hr_skill_descriptions_count = fields.Integer(string='Description Entries Count', compute='_compute_hr_skill_descriptions_count')
    active = fields.Boolean(default=True,string='Active')
    archived_skill_count = fields.Integer(string='Archived Skill Count', compute='_compute_archived_skill_count')

    @api.depends('skill_ids')
    def _compute_archived_skill_count(self):
        desc_data = self.env['hr.skill'].read_group([('active', '=', False)], ['active'], groupby=['skill_type_id'])
        mapped_data = dict([(dict_data['skill_type_id'][0], dict_data['skill_type_id_count']) for dict_data in desc_data])
        for r in self:
            r.archived_skill_count = mapped_data.get(r.id, 0)

    @api.depends('hr_skill_description_ids')
    def _compute_hr_skill_descriptions_count(self):
        desc_data = self.env['hr.skill.description'].read_group([('skill_type_id', 'in', self.ids)], ['skill_type_id'], ['skill_type_id'])
        mapped_data = dict([(dict_data['skill_type_id'][0], dict_data['skill_type_id_count']) for dict_data in desc_data])
        for r in self:
            r.hr_skill_descriptions_count = mapped_data.get(r.id, 0)

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        types = super(SkillRequirement, self).create(vals_list)
        types._synch_description()
        return types

    def write(self, vals):
        res = super(SkillRequirement, self).write(vals)
        self._synch_description()
        return res

    def _synch_description(self):
        existing_desc_records = self.env['hr.skill.description'].search([
            ('skill_type_id', 'in', self.ids),
            ('skill_id', 'in', self.skill_ids.ids),
            ('skill_level_id', 'in', self.skill_level_ids.ids)
            ])
        vals_list = []
        for r in self:
            for skill in r.skill_ids:
                for level in r.skill_level_ids:
                    if not existing_desc_records.filtered(
                        lambda rec: rec.skill_type_id.id == r.id \
                        and rec.skill_id.id == skill.id \
                        and rec.skill_level_id.id == level.id):
                        vals = {
                            'skill_type_id': r.id,
                            'skill_id': skill.id,
                            'skill_level_id': level.id
                            }
                        vals_list.append(vals)
        if vals_list:
            return self.env['hr.skill.description'].create(vals_list)
        return self.env['hr.skill.description']

    def action_view_description_entries(self):
        action = self.env['ir.actions.act_window']._for_xml_id('viin_hr_skill_framework.action_skill_description')
        action['context'] = {
            'default_skill_type_id': self[:1].id,
            }
        action['domain'] = "[('skill_type_id','in',%s)]" % self.ids
        return action

    def action_view_archive_skills(self):
        result = self.env['ir.actions.act_window']._for_xml_id('viin_hr_skill_framework.action_hr_skills')
        result['domain'] = "[('active','=',False)]"
        return result
