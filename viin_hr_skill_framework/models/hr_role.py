from odoo import models, fields, api


class HrRole(models.Model):
    _inherit = 'hr.role'

    skill_description_ids = fields.Many2many('hr.skill.description', compute='_compute_skill_description_ids',
                                             string='Required Skills',
                                             help="Minimum skills that the employees of this role are required to have.")
    skill_descriptions_count = fields.Integer(string='Skill Descriptions Count', compute='_compute_skill_description_ids')
    
    skill_report_ids = fields.One2many('hr.employee.skill.report', 'role_id', string='Skills Report Entries')
    skill_failure_report_count = fields.Integer(string='Skill Failure Report Count', compute='_compute_skill_failure_report_count')

    @api.depends('rank_ids.skill_description_ids')
    def _compute_skill_description_ids(self):
        for r in self:
            desc_entries = r.rank_ids[:1].skill_description_ids
            r.skill_description_ids = desc_entries
            r.skill_descriptions_count = len(desc_entries)

    def _compute_skill_failure_report_count(self):
        report_data = self.env['hr.employee.skill.report'].read_group([
            ('role_id', 'in', self.ids),
            ('reach_progress', '<', 100.0)], ['role_id'], ['role_id'])
        mapped_data = dict([(dict_data['role_id'][0], dict_data['role_id_count']) for dict_data in report_data])
        for r in self:
            r.skill_failure_report_count = mapped_data.get(r.id, 0)

    def action_view_required_skill_descriptions(self):
        action = self.env.ref('viin_hr_skill_framework.action_skill_description')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('id','in',%s)]" % self.skill_description_ids.ids
        return result

    def action_view_skill_report(self):
        action = self.env.ref('viin_hr_skill_framework.action_hr_employee_skill_report_report')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('id','in',%s)]" % self.skill_report_ids.ids
        return result

    def action_view_skill_failure_report(self):
        action = self.env.ref('viin_hr_skill_framework.action_hr_employee_skill_report_report')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('id','in',%s),('reach_progress','<',100.0)]" % self.skill_report_ids.ids
        return result

