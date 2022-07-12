from odoo import models, fields


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    overtime_plan_line_ids = fields.One2many('hr.overtime.plan.line', 'employee_id', string='Overtime Plan Lines')
    overtime_plan_ids = fields.One2many('hr.overtime.plan', 'employee_id', string='Overtime Plans')
    employee_overtime_ids = fields.One2many('hr.employee.overtime', 'employee_id', string='Overtime')
    employee_overtime_count = fields.Integer(string='Overtime Count', compute='_compute_employee_overtime_count')

    def _compute_employee_overtime_count(self):
        overtime_data = self.env['hr.employee.overtime'].read_group([('employee_id', 'in', self.ids)], ['employee_id'], ['employee_id'])
        mapped_data = dict([(dict_data['employee_id'][0], dict_data['employee_id_count']) for dict_data in overtime_data])
        for r in self:
            r.employee_overtime_count = mapped_data.get(r.id, 0)

    def action_view_overtime_report(self):
        result = self.env['ir.actions.actions']._for_xml_id('viin_hr_overtime.action_hr_employee_overtime_report')

        # override the context to get rid of the default filtering
        result['context'] = {'search_default_grp_rule':1}
        result['domain'] = "[('employee_id','in',%s)]" % str(self.ids)
        return result
