from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class ApprovalRequest(models.Model):
    _name = 'approval.request'
    _description = "Approval Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _mail_post_access = 'read'

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env.user.employee_id

    def _employee_id_domain(self):
        if self.user_has_groups('to_approvals.group_approval_officer'):
            return []
        return [('user_id', '=', self.env.user.id)]

    name = fields.Char(string='Name', required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))
    title = fields.Char(string='Title', required=True, tracking=True, readonly=False, states={'confirm': [('readonly', True)],
                                                                                              'validate1': [('readonly', True)],
                                                                                              'validate': [('readonly', True)],
                                                                                              'done': [('readonly', True)],
                                                                                              'refuse': [('readonly', True)],
                                                                                              'cancel': [('readonly', True)]})
    approval_type_id = fields.Many2one('approval.request.type', string="Approval Type", tracking=True,
                                   required=True, copy=True, readonly=False, states={'confirm': [('readonly', True)],
                                                                                     'validate1': [('readonly', True)],
                                                                                     'validate': [('readonly', True)],
                                                                                     'done': [('readonly', True)],
                                                                                     'refuse': [('readonly', True)],
                                                                                     'cancel': [('readonly', True)]})
    type = fields.Selection(string='Type', related='approval_type_id.type', readonly=True)  # This field is used for inheriting modules as a condition of hiding the view
    date = fields.Date(string='Request Date', required=True, default=fields.Date.today, copy=False,
                                 readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee, required=True, tracking=True,
                                    readonly=False, states={'confirm': [('readonly', True)],
                                                            'validate1': [('readonly', True)],
                                                            'validate': [('readonly', True)],
                                                            'done': [('readonly', True)],
                                                            'refuse': [('readonly', True)],
                                                            'cancel': [('readonly', True)]},
                                    domain=_employee_id_domain)
    involve_employee_ids = fields.Many2many('hr.employee', 'approval_request_hr_employee_rel', 'approval_id', 'employee_id',
                                            compute='_compute_involve_employee_ids', store=True,
                                            string='Involving Employees', help="Store employees that involve the approval request.")
    department_id = fields.Many2one('hr.department', string='Department', help="Select a department of employee",
                                    compute='_compute_department', readonly=False, store=True, copy=False,
                                    domain="[('company_id','=',company_id)]")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('validate1', 'First Approved'),
        ('validate', 'Approved'),
        ('done', 'Done'),
        ('refuse', 'Refused'),
        ('cancel', 'Cancelled')
        ], string='Status', tracking=True, copy=False, default='draft', readonly=False, states={'confirm': [('readonly', True)],
                                                                                                'validate1': [('readonly', True)],
                                                                                                'validate': [('readonly', True)],
                                                                                                'done': [('readonly', True)],
                                                                                                'refuse': [('readonly', True)],
                                                                                                'cancel': [('readonly', True)]}, group_expand='_expand_states')
    description = fields.Text(string='Description', copy=False, readonly=False, states={'confirm': [('readonly', True)],
                                                                                        'validate1': [('readonly', True)],
                                                                                        'validate': [('readonly', True)],
                                                                                        'done': [('readonly', True)],
                                                                                        'refuse': [('readonly', True)],
                                                                                        'cancel': [('readonly', True)]}, tracking=True)
    first_approver_id = fields.Many2one(
        'res.users', string='First Approval By', readonly=True, copy=False,
        help="This field is automatically filled by the user who validate the approval request")
    second_approver_id = fields.Many2one(
        'res.users', string='Second Approval By', readonly=True, copy=False,
        help="This field is automatically filled by the user who validate the approval request with second level (When approval request type requires second validation)")
    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')
    can_validate = fields.Boolean('Can Validate', compute='_compute_can_validate')
    can_done = fields.Boolean('Can Done', compute='_compute_can_mark_done')
    can_refuse = fields.Boolean('Can Refuse', compute='_compute_can_refuse')
    can_confirm = fields.Boolean('Can Confirm', compute='_compute_can_confirm')
    validation_type = fields.Selection(string="Validation", related='approval_type_id.validation_type', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company,
                                 readonly=False, states={'confirm': [('readonly', True)],
                                                         'validate1': [('readonly', True)],
                                                         'validate': [('readonly', True)],
                                                         'done': [('readonly', True)],
                                                         'refuse': [('readonly', True)],
                                                         'cancel': [('readonly', True)]}
                                 )

    def name_get(self):
        """
        name_get that supports displaying title with their name as prefix
        """
        result = []
        for r in self:
            result.append((r.id, "[%s] %s" % (r.name, r.title)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('title', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        request = self.search(domain + args, limit=limit)
        return request.name_get()

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.depends('employee_id')
    def _compute_department(self):
        for r in self:
            r.department_id = r.employee_id.contract_id.department_id if hasattr(r, 'contract_id') else r.employee_id.department_id

    @api.depends('employee_id')
    def _compute_can_approve(self):
        is_app_admin = self.env.user.has_group('to_approvals.group_approval_manager')
        managers_map = self._get_employee_managers_map()
        for r in self:
            if is_app_admin:
                r.can_approve = True
                continue
            r.can_approve = False
            responsible = r.approval_type_id.responsible_id
            if r.validation_type not in ('both', 'leader'):
                if r.env.uid == responsible.id:
                    r.can_approve = True
            else:
                if r.env.user.employee_id.id in managers_map[r.id].ids or r.env.uid == responsible.id:
                    r.can_approve = True

    @api.depends('employee_id')
    def _compute_can_validate(self):
        is_app_admin = self.env.user.has_group('to_approvals.group_approval_manager')
        for r in self:
            if is_app_admin:
                r.can_validate = True
                continue
            r.can_validate = False
            if r.validation_type == 'both':
                if r.env.uid == r.approval_type_id.responsible_id.id:
                    r.can_validate = True

    @api.depends('employee_id')
    def _compute_can_mark_done(self):
        is_app_admin = self.env.user.has_group('to_approvals.group_approval_manager')
        managers_map = self._get_employee_managers_map()
        for r in self:
            if is_app_admin:
                r.can_done = True
                continue
            r.can_done = False
            if r.validation_type == 'leader' and r.env.user.employee_id.id in managers_map[r.id].ids:
                    r.can_done = True
            elif r.validation_type == 'no_validation' and r.env.user == r.employee_id.user_id:
                    r.can_done = True
            else:
                if r.env.uid == r.approval_type_id.responsible_id.id:
                    r.can_done = True

    @api.depends('employee_id')
    def _compute_can_refuse(self):
        is_app_admin = self.env.user.has_group('to_approvals.group_approval_manager')
        managers_map = self._get_employee_managers_map()
        for r in self:
            if is_app_admin:
                r.can_refuse = True
                continue
            r.can_refuse = False
            responsible = r.approval_type_id.responsible_id.id
            if not is_app_admin:
                if r.validation_type == 'leader' and r.env.user.employee_id.id in managers_map[r.id].ids:
                        r.can_refuse = True
                elif r.validation_type == 'both':
                    if r.state in ['confirm', 'validate1'] and (r.env.user.employee_id.id in managers_map[r.id].ids or r.env.uid == responsible):
                            r.can_refuse = True
                    else:
                        if r.env.uid == responsible:
                            r.can_refuse = True
                else:
                    if r.env.uid == responsible:
                        r.can_refuse = True

    @api.depends('employee_id')
    def _compute_can_confirm(self):
        is_app_admin = self.env.user.has_group('to_approvals.group_approval_manager')
        managers_map = self._get_employee_managers_map()
        for r in self:
            if is_app_admin or r.employee_id.user_id.id == r.env.user.id:
                r.can_confirm = True
                continue
            r.can_confirm = False
            responsible = r.approval_type_id.responsible_id.id
            if r.validation_type == 'both' and (r.env.uid == responsible or r.env.user.employee_id.id in managers_map[r.id].ids):
                    r.can_confirm = True
            elif r.validation_type == 'leader' and r.env.user.employee_id.id in managers_map[r.id].ids:
                    r.can_confirm = True
            elif r.validation_type == 'hr' and r.env.uid == responsible:
                    r.can_confirm = True

    @api.depends('employee_id')
    def _compute_involve_employee_ids(self):
        for r in self:
            r.involve_employee_ids = [(6, 0, r._get_involve_employees().ids)]

    def _get_involve_employees(self):
        self.ensure_one()
        return self.employee_id

    def _get_employee_managers_map(self):
        """
        This get all the employee's managers including all the superior and the manager of the employee department, excluding himself.
        """
        all_employees = self.env['hr.employee'].search([])
        res = {}
        for r in self:
            res[r.id] = all_employees.filtered(
                lambda emp: r.employee_id.id in emp.subordinate_ids.ids \
                    or (r.employee_id != emp and r.department_id.manager_id == emp) \
                    or (r.employee_id == emp and r.department_id.parent_id.manager_id == emp)
                )
        return res

    def action_confirm(self):
        self = self.sudo().with_context(approval_action_call=True)
        for r in self:
            if not r.can_confirm:
                raise UserError(_("You do not have access right to confirm the request '%s'") % r.display_name)
            if r.state != 'draft':
                raise UserError(_("The approval request '%s' must be in Draft state in order to get confirmed.") % r.display_name)
        self.write({'state': 'confirm'})
        approvals = self.filtered(lambda x: x.validation_type == 'no_validation')
        approval_sudo = approvals.sudo()
        if approvals:
            approvals.with_context(bypass_check=True).action_validate()
            approval_sudo.message_subscribe(partner_ids=[approval_sudo._get_responsible_for_approval().partner_id.id])
            approval_sudo.message_post(body=_("The request has been automatically approved"), subtype="mt_comment")  # Message from OdooBot (sudo)
        self.activity_update()

    def action_approve(self):
        self = self.with_context(approval_action_call=True)
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        for r in self:
            if not r.can_approve:
                raise UserError(_("You do not have access right to approve the request '%s'") % r.display_name)
            if r.state != 'confirm':
                raise UserError(_("The approval request '%s' must be confirmed  in order to get approved.") % r.display_name)
        self.filtered(lambda x: x.validation_type == 'both').write({'state': 'validate1', 'first_approver_id': self.env.user.id})
        # Post a second message, more verbose than the tracking message
        for r in self.filtered(lambda x: x.sudo().employee_id.user_id):
            r.message_post(
                body=_("Your request '%s' has been accepted") % r.display_name,
                partner_ids=r.employee_id.user_id.partner_id.ids)
        self.filtered(
            lambda x: x.validation_type != 'both' or x.approval_type_id.responsible_id.id == self.env.uid
                ).with_context(bypass_check=True).action_validate()
        self.activity_update()

    def action_validate(self):
        self = self.with_context(approval_action_call=True)
        for r in self:
            if not r.can_validate and not self.env.context.get('bypass_check'):
                raise UserError(_("You do not have access right to validate the request '%s'") % r.display_name)
            if r.state not in ['confirm', 'validate1']:
                raise UserError(_("The approval request '%s' state must be 'Confirm' or 'First Approved' in order to get validated.") % r.display_name) 
        self.write({'state': 'validate'})

        self.filtered(lambda x: x.validation_type == 'both').write({'second_approver_id': self.env.user.id})
        self.filtered(lambda x: x.validation_type != 'both').write({'first_approver_id': self.env.user.id})

        for r in self.filtered(lambda x: x.sudo().employee_id.user_id):
            r.message_post(
                body=_("Your request '%s' has been validated") % r.display_name,
                partner_ids=r.sudo().employee_id.user_id.partner_id.ids)
        self.activity_update()

    def action_done(self):
        self = self.with_context(approval_action_call=True)
        for r in self:
            if not r.can_done:
                raise UserError(_("You do not have access right to mark as done the request '%s'") % r.display_name)
            if r.state != 'validate':
                raise UserError(_("The approval request '%s' must be validated in order to mark as done it.") % r.display_name)
            if r.sudo().employee_id.user_id:
                r.message_post(
                    body=_("Your request '%s' has been done") % r.display_name,
                    partner_ids=r.employee_id.user_id.partner_id.ids)
        self.activity_update()
        self.write({'state': 'done'})

    def action_refuse(self):
        self = self.with_context(approval_action_call=True)
        for r in self:
            if not r.can_refuse:
                raise UserError(_("You do not have access right to refuse the request '%s'") % r.display_name)
            if r.state in ['draft', 'refuse', 'cancel']:
                raise UserError(_("The approval request '%s' state must be 'Confirmed', 'First Approved', 'Approved', 'Done' in order to refuse it.") % r.display_name)
        validated_approvals = self.filtered(lambda x: x.state == 'validate1')
        validated_approvals.write({'state': 'refuse', 'first_approver_id': False})
        (self - validated_approvals).write({'state': 'refuse', 'second_approver_id': False})
        # Post a second message, more verbose than the tracking message
        for r in self:
            if r.sudo().employee_id.user_id:
                r.message_post(
                    body=_("Your request '%s' has been refused") % r.display_name,
                    partner_ids=r.employee_id.user_id.partner_id.ids)
        self.activity_update()
        return True

    def action_cancel(self):
        self = self.with_context(approval_action_call=True)
        for r in self:
            if not r.can_confirm:
                raise UserError(_("You do not have access right to cancel the request '%s'") % r.display_name)
            if r.state not in ['draft', 'confirm']:
                raise UserError(_("The approval request '%s' state must be 'Draft' or 'Confirmed' in order to cancel it.") % r.display_name)  
        self.write({'state':'cancel'})
        self.activity_update()

    def action_draft(self):
        self = self.with_context(approval_action_call=True)
        for r in self:
            if not r.can_confirm:
                raise UserError(_("You do not have access right to reset the request '%s'") % r.display_name)
            if r.state not in ['refuse', 'cancel']:
                raise UserError(_("The approval request '%s' state must be 'Refused' or 'Cancel' in order to be reset to draft.") % r.display_name)   
        self.write({'state':'draft'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('approval.request')
        requests = super(ApprovalRequest, self).create(vals_list)
        requests.sudo().add_follower()
        return requests
    
    def write(self, vals):
        # Force using action to status control instread of direct writing state
        if 'state' in vals and not self._context.get('approval_action_call', False):
            state_change = self.filtered(lambda a: a.state != vals['state'])
            if vals['state'] == 'draft':
                state_change.action_draft()
            elif vals['state'] == 'confirm':
                state_change.action_confirm()
            elif vals['state'] == 'validate1':
                state_change.action_approve()
            elif vals['state'] == 'validate':
                state_change.action_validate()
            elif vals['state'] == 'done':
                state_change.action_done()
            elif vals['state'] == 'refuse':
                state_change.action_refuse()
            elif vals['state'] == 'cancel':
                state_change.action_cancel()
            else:
                raise ValidationError(_("Invalid status %s") % (vals['state'],))
            del vals['state']
        return super(ApprovalRequest, self).write(vals)

    def unlink(self):
        for item in self:
            if item.state != 'draft':
                raise UserError(_("You can only delete records which are in draft status."))
        return super(ApprovalRequest, self).unlink()

    def add_follower(self):
        for r in self:
            if r.employee_id.user_id:
                r.message_subscribe(partner_ids=r.employee_id.user_id.partner_id.ids)

    def _get_responsible_for_approval(self):
        self.ensure_one()
        responsible = self.env['res.users'].browse(SUPERUSER_ID)
        group_approval_manager = self.env.ref('to_approvals.group_approval_manager')
        user_admin = group_approval_manager.users[:1]
        if self.validation_type == 'leader' or (self.validation_type == 'both' and self.state == 'confirm'):
            responsible = self.employee_id.parent_id.user_id or self.employee_id.department_id.manager_id.user_id or user_admin
        elif self.validation_type == 'hr' or (self.validation_type == 'both' and self.state == 'validate1'):
            if self.approval_type_id.responsible_id:
                responsible = self.approval_type_id.responsible_id
        return responsible

    def activity_update(self):
        to_clean, to_do = self.env['approval.request'], self.env['approval.request']
        for approval in self:
            note = _("New %s Request created by %s") % (approval.approval_type_id.name, approval.create_uid.name)
            if approval.state == 'draft':
                to_clean |= approval
            elif approval.state == 'confirm':
                approval.activity_schedule(
                    'to_approvals.mail_act_approval',
                    note=note,
                    user_id=approval.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif approval.state == 'validate1':
                approval.activity_feedback(['to_approvals.mail_act_approval'])
                approval.activity_schedule(
                    'to_approvals.mail_act_second_approval',
                    note=note,
                    user_id=approval.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif approval.state == 'validate':
                to_do |= approval
            elif approval.state in ('refuse', 'cancel'):
                to_clean |= approval
        if to_clean:
            to_clean.activity_unlink(['to_approvals.mail_act_approval', 'to_approvals.mail_act_second_approval'])
        if to_do:
            to_do.activity_feedback(['to_approvals.mail_act_approval', 'to_approvals.mail_act_second_approval'])
