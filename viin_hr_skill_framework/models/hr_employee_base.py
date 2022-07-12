from odoo import models, fields, api


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    job_position_skills_required = fields.Boolean(string='Job Position\'s Skills Required',
                                                  help="If enabled, all the skills required by the corresponding"
                                                  " job position will also be applied to the employee. Otherwise, only"
                                                  " the skills required by the matched rank (if any) will be applied.")
    skill_description_ids = fields.Many2many('hr.skill.description', 'employee_skill_description_required_rel',
                                             'employee_id', 'skill_description_id',
                                             compute='_compute_skill_description_ids', store=True,
                                             string='Required Skills',
                                             help="Technical field that stores the skills that the employee is required to have.")
    skill_descriptions_count = fields.Integer(string='Required Skills Count', compute='_compute_skill_descriptions_count')
    preferred_skill_description_ids = fields.Many2many('hr.skill.description', 'employee_skill_description_preferred_rel',
                                                       'employee_id', 'skill_description_id',
                                                       compute='_compute_preferred_skill_description_ids', store=True,
                                                       string='Preferred Skills',
                                                       help="Technical field that stores the skills that the employee is preferred to have.")
    preferred_skill_descriptions_count = fields.Integer(string='Preferred Skills Count', compute='_compute_preferred_skill_descriptions_count')
    skill_report_ids = fields.One2many('hr.employee.skill.report', 'employee_id',
                                       string='Skills Report Entries', help="Status report of all the required and preferred skills of the current employee.")
    skills_report_entries_count = fields.Integer(string='Skills Requirement Count', compute='_compute_skills_report_entries_count')
    unmet_skill_report_ids = fields.One2many('hr.employee.skill.report', 'employee_id',
                                             domain="[('expectation','=','required'),('reach_progress','<',100.0)]",
                                             string='Unmet Skills', help="Show required skills that the employee is currently failed to meet.")
    unmet_skills_report_entries_count = fields.Integer(string='Unmet Skills Count', compute='_compute_unmet_skills_report_entries_count')

    @api.depends('job_position_skills_required', 'job_id.skill_description_ids', 'rank_id.skill_description_ids')
    def _compute_skill_description_ids(self):
        for r in self:
            if r.job_position_skills_required and r.rank_id:
                r.skill_description_ids = r.job_id.skill_description_ids | r.rank_id.skill_description_ids
            elif r.job_position_skills_required:
                r.skill_description_ids = r.job_id.skill_description_ids
            elif r.rank_id:
                r.skill_description_ids = r.rank_id.skill_description_ids
            else:
                r.skill_description_ids = False

    @api.depends('skill_description_ids')
    def _compute_skill_descriptions_count(self):
        for r in self:
            r.skill_descriptions_count = len(r.skill_description_ids)

    @api.depends('job_id.preferred_skill_description_ids', 'rank_id.preferred_skill_description_ids')
    def _compute_preferred_skill_description_ids(self):
        for r in self:
            if r.preferred_skill_description_ids and r.rank_id:
                r.preferred_skill_description_ids = r.job_id.preferred_skill_description_ids | r.rank_id.preferred_skill_description_ids
            elif r.job_position_skills_required:
                r.preferred_skill_description_ids = r.job_id.preferred_skill_description_ids
            elif r.rank_id:
                r.preferred_skill_description_ids = r.rank_id.preferred_skill_description_ids
            else:
                r.preferred_skill_description_ids = False

    @api.depends('preferred_skill_description_ids')
    def _compute_preferred_skill_descriptions_count(self):
        for r in self:
            r.preferred_skill_descriptions_count = len(r.preferred_skill_description_ids)

    @api.depends('skill_report_ids')
    def _compute_skills_report_entries_count(self):
        report_data = self.env['hr.employee.skill.report'].read_group([('employee_id', 'in', self.ids)], ['employee_id'], ['employee_id'])
        mapped_data = dict([(dict_data['employee_id'][0], dict_data['employee_id_count']) for dict_data in report_data])
        for r in self:
            r.skills_report_entries_count = mapped_data.get(r.id, 0)

    @api.depends('unmet_skill_report_ids')
    def _compute_unmet_skills_report_entries_count(self):
        report_data = self.env['hr.employee.skill.report'].read_group([
            ('expectation', '=', 'required'),
            ('reach_progress', '<', 100.0)
            ], ['employee_id'], ['employee_id'])
        mapped_data = dict([(dict_data['employee_id'][0], dict_data['employee_id_count']) for dict_data in report_data])
        for r in self:
            r.unmet_skills_report_entries_count = mapped_data.get(r.id, 0)

    def action_view_required_skill_descriptions(self):
        action = self.env.ref('viin_hr_skill_framework.action_skill_description')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('id','in',%s)]" % self.skill_description_ids.ids
        return result

    def action_view_preferred_skill_descriptions(self):
        action = self.env.ref('viin_hr_skill_framework.action_skill_description')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('id','in',%s)]" % self.preferred_skill_description_ids.ids
        return result

    def action_view_skill_reports(self):
        action = self.env.ref('viin_hr_skill_framework.action_hr_employee_skill_report_report')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('employee_id','in',%s)]" % self.ids
        return result

    def action_view_unmet_skill_report(self):
        action = self.env.ref('viin_hr_skill_framework.action_hr_employee_skill_report_report')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('employee_id','in',%s),('expectation','=','required'),('reach_progress','<',100.0)]" % self.ids
        return result
