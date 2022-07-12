from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    overtime_plan_ids = fields.One2many('hr.overtime.plan', 'approval_id', string='Overtime Planning Registrations',
                                                 readonly=True, states={'draft':[('readonly', False)]}, auto_join=True)
    overtime_plan_line_ids = fields.One2many('hr.overtime.plan.line', 'approval_id', string='Overtime Plan', readonly=True)
    overtime_plan_lines_count = fields.Integer(string='Overtime Plan Lines Count', compute='_compute_overtime_plan_lines_count')

    def unlink(self):
        self.overtime_plan_ids.with_context(force_delete=True).unlink()
        return super(ApprovalRequest, self).unlink()

    @api.depends('overtime_plan_ids.employee_id')
    def _compute_involve_employee_ids(self):
        super(ApprovalRequest, self)._compute_involve_employee_ids()

    def _compute_overtime_plan_lines_count(self):
        overtime_data = self.env['hr.overtime.plan.line'].read_group([('approval_id', 'in', self.ids)], ['approval_id'], ['approval_id'])
        mapped_data = dict([(dict_data['approval_id'][0], dict_data['approval_id_count']) for dict_data in overtime_data])
        for r in self:
            r.overtime_plan_lines_count = mapped_data.get(r.id, 0)

    @api.depends('approval_type_id', 'state', 'overtime_plan_ids')
    def _check_if_empty_lines(self):
        super(ApprovalRequest, self)._check_if_empty_lines()
        for r in self:
            if r.state != 'draft' and r.type == 'overtime' and not r.overtime_plan_ids:
                raise UserError(_("There is no overtime plan on the request `%s` for approval") % r.display_name)

    def _get_involve_employees(self):
        self.ensure_one()
        # we don't care the self.employee_id as it makes no sense for an overtime approval request
        if self.type == 'overtime':
            employees = self.overtime_plan_ids.employee_id
        else:
            employees = super(ApprovalRequest, self)._get_involve_employees()
        return employees

    def action_view_overtime_plan_lines(self):
        action = self.env['ir.actions.actions']._for_xml_id('viin_hr_overtime.action_hr_overtime_plan_line')
        # override the context to get rid of the default filtering
        action['context'] = {'search_default_grp_employee':1}
        action['domain'] = "[('approval_id', 'in', %s)]" % str(self.ids)
        return action

    def action_confirm(self):
        for r in self:
            r.message_subscribe(partner_ids=r.sudo().involve_employee_ids.user_id.partner_id.ids)
        for plan in self.overtime_plan_ids:
            employee_partner = plan.sudo().employee_id.user_id.partner_id
            if employee_partner:
                plan.message_subscribe(partner_ids=[employee_partner.id])
        super(ApprovalRequest, self).action_confirm()

    def action_mass_registration(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('viin_hr_overtime.action_hr_overtime_request_mass_window')
        action['context'] = {'default_approval_required': True, 'default_approval_id': self.id}
        return action

    def action_refuse(self):
        if self.overtime_plan_ids:
            self.overtime_plan_ids.with_context(ignore_overtime_approval_state_exception=True).action_refuse()
        super(ApprovalRequest, self).action_refuse()

    def action_cancel(self):
        if self.overtime_plan_ids:
            self.overtime_plan_ids.with_context(ignore_overtime_approval_state_exception=True).action_cancel()
        super(ApprovalRequest, self).action_cancel()

    def action_done(self):
        super(ApprovalRequest, self).action_done()
        if self.overtime_plan_ids:
            self.overtime_plan_ids.sudo()._recognize_actual_overtime()

    def action_recompute_overtime_plans(self):
        self.overtime_plan_ids.action_recompute_plan_lines()
