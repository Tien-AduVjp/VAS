# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # TODO: master/14+ make these fields available in both employee and employee public
    user_assignment_ids = fields.One2many('user.assignment', 'employee_id', string='Assignments', readonly=True)
    user_assignments_count = fields.Integer(string='Assignments Count', compute='_compute_user_assignments_count')

    def _compute_user_assignments_count(self):
        assignment_data = self.env['user.assignment'].read_group([('employee_id', 'in', self.ids)], ['employee_id'], ['employee_id'])
        mapped_data = dict([(dict_data['employee_id'][0], dict_data['employee_id_count']) for dict_data in assignment_data])
        for r in self:
            r.user_assignments_count = mapped_data.get(r.id, 0)

    def action_view_assignments(self):
        action = self.env['ir.actions.act_window']._for_xml_id('viin_user_assignment_log.action_user_assignment')
        action['context'] = {}
        action['domain'] = "[('employee_id', 'in', %s)]" % str(self.ids)
        return action
