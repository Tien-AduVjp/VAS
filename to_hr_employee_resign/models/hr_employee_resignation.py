from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrEmployeeResignation(models.Model):
    _name = 'hr.employee.resignation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Resignation'

    name = fields.Char(string='Ref.', readonly=True, required=True, default='New')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, 
                            readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')], string='Status', required=True, default='draft', index=True, tracking=True)
    reason = fields.Text(string='Reason')
    date_resign = fields.Date(string='Date Resign', tracking=True, index=True, required=True, 
                            readonly=True, states={'draft': [('readonly', False)]},
                              help='The date on which all the contracts of the employee will be terminated')
    date_approved = fields.Datetime(string='Date Approved', readonly=True, tracking=True, index=True)
    plan_id = fields.Many2one('hr.plan', string="Plan", required=True, domain=[('is_offboarding', '=', True)],
                              compute='_compute_plan_id', readonly=False, store=True,
                              states={'submitted': [('readonly', True)],
                                        'approved': [('readonly', True)],
                                        'refused': [('readonly', True)],
                                        'done': [('readonly', True)],
                                        'cancelled': [('readonly', True)]})
    activity_ids = fields.One2many('mail.activity' ,'employee_resign_id', string="Activities")

    @api.depends('employee_id')
    def _compute_plan_id(self):
        HrPlan = self.env['hr.plan']
        for r in self:
            plan_id = False
            if r.employee_id:
                resign_plans = HrPlan.search([('is_offboarding', '=', True)])
                resign_department_plan = resign_plans.filtered(lambda rs: rs.department_id == r.employee_id.department_id)
                if resign_department_plan:
                    plan_id = resign_department_plan[0]
                elif resign_plans:
                    resign_plans_no_department = resign_plans.filtered(lambda rs: not rs.department_id)
                    plan_id = resign_plans_no_department[0] if resign_plans_no_department else False
            r.plan_id = plan_id

    def action_submit(self):
        for r in self:
            if r.state != 'draft':
                raise UserError(_("You can submit draft resignations only!"))
        self.write({'state':'submitted'})
 
    def action_refuse(self):
        self.write({'state':'refused'})
 
    def action_approve(self):
        HrEmployee = self.env['hr.employee']
        MailActivity = self.env['mail.activity']
        for r in self:
            if r.state not in ('refused', 'submitted'):
                raise UserError(_("You can only approve the resignations that are in either Refused state or Submitted state!"))
            data = {
                'date_approved':fields.Datetime.now(),
                'state':'approved'
            }
            r.write(data)
            for activity_type in r.plan_id.plan_activity_type_ids:
                responsible = activity_type.get_responsible_id(self.employee_id)
    
                if HrEmployee.with_user(responsible).check_access_rights('read', raise_exception=False):
                    date_deadline = MailActivity._calculate_date_deadline(activity_type.activity_type_id)
                    self.env['mail.activity'].create({
                        'res_id': self.employee_id.id,
                        'res_model_id': self.env['ir.model']._get('hr.employee').id,
                        'summary': activity_type.summary,
                        'note': activity_type.note,
                        'activity_type_id': activity_type.activity_type_id.id,
                        'user_id': responsible.id,
                        'date_deadline': date_deadline,
                        'employee_resign_id': r.id
                    })

    def action_cancel(self):
        for r in self:
            if r.state not in ('approved', 'submitted'):
                raise UserError(_("You can only cancel the resignations that are in either Approved state or Submitted state!"))
        self.write({
            'state':'cancelled',
            'date_approved': False
            })
        self.activity_ids.unlink()
 
    def action_done(self):
        for r in self:
            if r.state != 'approved':
                raise UserError(_("You can only set done the resignations that are Approved state!"))
            r.employee_id.write({'active':False})
        self.write({'state':'done'})
 
    def action_done_to_approved(self):
        for r in self:
            if r.state != 'done':
                raise UserError(_("You can revert Done resignations to Approved state only if the resignations are in Done state!"))
        self.write({'state':'approved'})
 
    def action_draft(self):
        for r in self:
            if r.state not in ('cancelled', 'refused'):
                raise UserError(_("You can only set draft the resignations that are in Cancelled or Refused state!"))
        self.write({'state':'draft'})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
               'hr.employee.resignation') or 'New'
        result = super(HrEmployeeResignation, self).create(vals)
        return result
 
    def unlink(self):
        for r in self:
            if r.state != 'draft':
                raise UserError(_("You may not be able to delete the employee resignation '%s' which is not in Draft state. You may need to set it to Draft first") % (r.name,))
        return super(HrEmployeeResignation, self).unlink()
