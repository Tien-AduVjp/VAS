from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import relativedelta
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
        elif self.user_has_groups('to_approvals.group_approval_team_leader'):
            # search for subordinates.
            # We could not be able to use the field `employee.subordinates` as it
            # may not consider `employee.department_id.manager_id` as a manager
            vals_list = self.env['hr.employee'].sudo().search_read([], ['parent_ids'])
            ids_list = [vals['id'] for vals in vals_list if self.env.user.employee_id.id in vals['parent_ids']]
            # add the current user's employee to the list
            ids_list.append(self.env.user.employee_id.id)
            return [('id', 'in', ids_list)]
        else:
            return [('user_id', '=', self.env.user.id)]

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    title = fields.Char(string='Title', required=True, tracking=True, readonly=False, copy=False, default=lambda self: _('New'),
                        states={
                            'confirm': [('readonly', True)],
                            'validate': [('readonly', True)],
                            'done': [('readonly', True)],
                            'refuse': [('readonly', True)],
                            'cancel': [('readonly', True)]}
                        )
    approval_type_id = fields.Many2one('approval.request.type', string='Approval Type', tracking=True,
                                   required=True, copy=True, readonly=False,
                                   states={
                                       'confirm': [('readonly', True)],
                                       'validate': [('readonly', True)],
                                       'done': [('readonly', True)],
                                       'refuse': [('readonly', True)],
                                       'cancel': [('readonly', True)]}
                                   )
    type = fields.Selection(string='Type', related='approval_type_id.type', store=True)
    mimimum_approvals = fields.Integer(string='Minimum Approvals', compute='_compute_mimimum_approvals', store=True)
    progress = fields.Float(string='Approval Progress', compute='_compute_progress',
                            store=True, group_operator="avg",
                            help="Approval progress of the current request in percentages.")
    date = fields.Date(string='Request Date', required=True, default=fields.Date.today, copy=False,
                                 readonly=True)
    deadline = fields.Date(string='Deadline', compute='_compute_deadline', store=True, readonly=False, required=True,
                           tracking=True,
                           help="The date by which this request should get fully approved.")
    approved_date = fields.Datetime('Approved Date', compute='_compute_approved_date', store=True,
                                    help="The date and time at which the request got fully approved.")
    forcing_approver_id = fields.Many2one('res.users', string='Forcing Approver', readonly=True, copy=False,
                                          help="The user who forced the request to be approved without waiting for others' action.")
    employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee, required=True, tracking=True,
                                    readonly=False, states={'confirm': [('readonly', True)],
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
                                    domain="[('company_id','=',company_id)]",
                                    states={'confirm': [('readonly', True)],
                                            'validate': [('readonly', True)],
                                            'done': [('readonly', True)],
                                            'refuse': [('readonly', True)],
                                            'cancel': [('readonly', True)]})

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'To Approve'),
        ('validate', 'Approved'),
        ('done', 'Done'),
        ('refuse', 'Refused'),
        ('cancel', 'Cancelled')
        ], string='Status', tracking=True, index=True, copy=False, default='draft', compute='_compute_state', store=True,
        readonly=False,
        states={
            'confirm': [('readonly', True)],
            'validate': [('readonly', True)],
            'done': [('readonly', True)],
            'refuse': [('readonly', True)],
            'cancel': [('readonly', True)]
            }, group_expand='_expand_states')
    my_state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('none', 'Not involved')
        ], string='My Approval Status', compute='_compute_my_state', search='_search_my_state')

    description = fields.Text(string='Description', copy=False, tracking=True, readonly=False,
                              states={
                                  'confirm': [('readonly', True)],
                                  'validate': [('readonly', True)],
                                  'done': [('readonly', True)],
                                  'refuse': [('readonly', True)],
                                  'cancel': [('readonly', True)]
                                  }
                              )
    can_confirm = fields.Boolean('Can Confirm', compute='_compute_can_confirm')
    can_validate = fields.Boolean('Can Approve', compute='_compute_can_validate')
    can_force_validate = fields.Boolean('Can Force Approval', compute='_compute_can_force_validate')
    can_refuse = fields.Boolean('Can Refuse', compute='_compute_can_refuse')
    can_done = fields.Boolean('Can Done', compute='_compute_can_mark_done')
    can_cancel = fields.Boolean('Can Cancel', compute='_compute_can_cancel')
    can_draft = fields.Boolean('Can Draft', compute='_compute_can_draft')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company,
                                 readonly=False, states={'confirm': [('readonly', True)],
                                                         'validate': [('readonly', True)],
                                                         'done': [('readonly', True)],
                                                         'refuse': [('readonly', True)],
                                                         'cancel': [('readonly', True)]}
                                 )
    currency_id = fields.Many2one('res.currency', string='Currency', compute='_compute_currency_id', store=True, readonly=False, required=True,
                                  states={
                                      'confirm': [('readonly', True)],
                                      'validate': [('readonly', True)],
                                      'done': [('readonly', True)],
                                      'refuse': [('readonly', True)],
                                      'cancel': [('readonly', True)],
                                    })
    show_currency_field = fields.Boolean(string='Show Currency', compute='_compute_show_currency_field')
    request_approval_user_line_ids = fields.One2many('request.approval.user.line', 'approval_id', string='Request Approvers',
                                        compute='_compute_request_approval_user_line_ids', store=True,
                                        readonly=lambda env: not env.user.has_group('to_approvals.group_approval_manager'),
                                        states={
                                            'confirm':[('readonly', True)],
                                            'validate': [('readonly', True)],
                                            'done': [('readonly', True)],
                                            'refuse': [('readonly', True)],
                                            'cancel': [('readonly', True)]
                                            })
    approver_ids = fields.Many2many('res.users', 'approval_request_res_users_rel', 'approval_request_id', 'user_id',
                                    string='Approvers', compute='_compute_approvers', store=True)
    last_approver_id = fields.Many2one('res.users', string='Last Approver', compute='_compute_last_approver_id', store=True)
    next_approver_id = fields.Many2one('res.users', string='Next Approver', compute='_compute_next_approver_id', store=True)

    def _expand_states(self, states, domain, order):
        return [key for key, _ in type(self).state.selection]

    @api.depends('company_id')
    def _compute_currency_id(self):
        for r in self:
            r.currency_id = r.company_id.currency_id

    @api.depends('employee_id')
    def _compute_department(self):
        hasattr_contract_id = hasattr(self, 'contract_id')
        for r in self:
            # if hr_contract is install, use contract's department
            department = False
            if hasattr_contract_id:
                r.department_id = r.employee_id.contract_id.department_id
            if not department:
                department = r.employee_id.department_id
            r.department_id = department

    @api.depends('approval_type_id', 'employee_id')
    def _compute_mimimum_approvals(self):
        for r in self:
            minium_approvals = r.approval_type_id.mimimum_approvals
            manager_user = r.employee_id._get_recursive_parents().filtered(
                lambda emp: emp.user_id and emp.user_id.has_group('to_approvals.group_approval_team_leader')
                )[:1].user_id
            if r.approval_type_id.manager_approval == 'required' and r.approval_type_id.type_approval_user_line_ids.filtered(lambda l: l.user_id == manager_user and l.required) and minium_approvals > 1:
                minium_approvals -= 1
            r.mimimum_approvals = minium_approvals

    @api.depends('approval_type_id')
    def _compute_deadline(self):
        for r in self:
            r.deadline = r.approval_type_id._get_deadline()

    @api.depends('employee_id', 'approval_type_id')
    def _compute_request_approval_user_line_ids(self):
        for r in self:
            cmd = [(3, l.id) for l in r.request_approval_user_line_ids]
            for vals in r._prepare_request_approval_user_line_vals_list():
                cmd += [(0, 0, vals)]
            r.request_approval_user_line_ids = cmd

    @api.depends('mimimum_approvals', 'request_approval_user_line_ids.state')
    def _compute_progress(self):
        for r in self:
            if r.mimimum_approvals <= 0:
                r.progress = 100.0
                continue

            # get lines of required approvers and non-required approvers
            required_approvers = r.request_approval_user_line_ids.filtered(lambda rec: rec.required)
            non_required_approvers = r.request_approval_user_line_ids.filtered(lambda rec: not rec.required)

            # count required number of required approvers and non-required approvers who will have to approve
            required_approvers_count = len(required_approvers)
            non_required_approvers_to_approve = r.mimimum_approvals - required_approvers_count

            # get percentage of required and non-required approvers against minimum approvals
            required_approvers_rate = required_approvers_count / r.mimimum_approvals
            none_required_approvers_rate = non_required_approvers_to_approve / r.mimimum_approvals

            # calculate progress of required and non-required approvals
            progress = 0.0
            if required_approvers_count:
                progress += required_approvers.mapped('state').count('approved') * required_approvers_rate / required_approvers_count
            if non_required_approvers_to_approve > 0:
                progress += non_required_approvers.mapped('state').count('approved') * none_required_approvers_rate / non_required_approvers_to_approve

            r.progress = progress * 100

    @api.depends('request_approval_user_line_ids.user_id')
    def _compute_approvers(self):
        for r in self:
            r.approver_ids = r.request_approval_user_line_ids.user_id

    @api.depends('request_approval_user_line_ids.user_id', 'request_approval_user_line_ids.state')
    def _compute_last_approver_id(self):
        for r in self:
            users_approved = r.request_approval_user_line_ids.filtered(
                lambda rec: rec.state == 'approved'
                ).sorted(lambda rec: (rec.date, rec.sequence, rec.id))
            r.last_approver_id = users_approved[-1].user_id if users_approved else False

    @api.depends(
        'request_approval_user_line_ids.user_id',
        'request_approval_user_line_ids.state',
        'request_approval_user_line_ids.required')
    def _compute_next_approver_id(self):
        for r in self:
            r.next_approver_id = r._get_next_approver()

    @api.depends('request_approval_user_line_ids.state', 'request_approval_user_line_ids.required', 'progress')
    def _compute_state(self):
        for r in self:
            all_approvers_count = len(r.request_approval_user_line_ids)
            required_approvers = r.request_approval_user_line_ids.filtered(lambda rec: rec.required)
            non_required_approvers = r.request_approval_user_line_ids.filtered(lambda rec: not rec.required)
            required_approver_states = required_approvers.mapped('state')
            required_approved_count = required_approver_states.count('approved')
            user_processed_count = len(r.request_approval_user_line_ids.filtered(lambda l: l.state in ('approved', 'refused')))
            user_not_refuse = len(r.request_approval_user_line_ids.filtered(lambda l: l.state not in ('refused', 'draft')))
            if not r.employee_id or not r.approval_type_id or all(state == 'draft' for state in r.request_approval_user_line_ids.mapped('state')):
                r.state = 'draft'  # for UI
            else:
                if 'refused' in required_approver_states or (user_processed_count == all_approvers_count and r.progress < 100.0) or \
                    (not required_approvers and user_not_refuse < r.mimimum_approvals and r.state != 'draft'):
                    r.state = 'refuse'
                elif all(state == 'pending' for state in r.request_approval_user_line_ids.mapped('state')) or \
                    (
                        any(state == 'pending' for state in non_required_approvers.mapped('state')) \
                        and (user_processed_count < all_approvers_count and r.progress < 100.0)
                        ) or any(state == 'pending' for state in required_approvers.mapped('state')):
                    r.state = 'confirm'
                elif len(required_approvers) == required_approved_count and r.progress >= 100.0:
                    r.state = 'validate'
                else:
                    r.state = r.state

    @api.depends('state')
    def _compute_approved_date(self):
        now = fields.Datetime.now()
        for r in self:
            if r.state == 'validate':
                r.approved_date = now
            elif r.state == 'done':
                r.approved_date = r.approved_date
            else:
                r.approved_date = False

    @api.depends('employee_id')
    def _compute_involve_employee_ids(self):
        for r in self:
            r.involve_employee_ids = [(6, 0, r._get_involve_employees().ids)]

    @api.depends('approval_type_id.type')
    def _compute_show_currency_field(self):
        for r in self:
            r.show_currency_field = False

    @api.depends_context('uid')
    @api.depends('request_approval_user_line_ids.user_id', 'request_approval_user_line_ids.state')
    def _compute_my_state(self):
        self.flush()
        # read group, by pass ORM for performance
        self.env.cr.execute(
            """
            SELECT r.id AS approval_id, l.state AS my_state
            FROM request_approval_user_line AS l
            JOIN approval_request AS r ON r.id = l.approval_id
            WHERE r.id in %s
                AND l.user_id = %s
            """,
            (
                tuple(self.ids or [0]),  # [0] to avoid SQL syntax error when self.ids is an empty list that causes `WHERE r.id in ()`
                self.env.uid
                )
            )
        data = self.env.cr.dictfetchall()
        mapped_data = dict([(dict_data['approval_id'], dict_data['my_state']) for dict_data in data])
        for r in self:
            r.my_state = mapped_data.get(r.id, 'none')

    @api.depends_context('uid')
    @api.depends('state', 'employee_id.user_id', 'create_uid')
    def _compute_can_confirm(self):
        is_app_admin = self.env.user.has_group('to_approvals.group_approval_manager')
        for r in self:
            if r.state != 'draft':
                r.can_confirm = False
            elif is_app_admin or r._check_is_owner() or r._check_is_manager():
                r.can_confirm = True
            else:
                r.can_confirm = False

    @api.depends_context('uid')
    @api.depends(
        'state',
        'request_approval_user_line_ids.user_id',
        'request_approval_user_line_ids.state',
        'approval_type_id.sequential_approvals')
    def _compute_can_validate(self):
        for r in self:
            if r.state not in ('confirm', 'refuse') or r.env.user.id in r.request_approval_user_line_ids.filtered(
                lambda l: l.state not in ('pending', 'refused')
                ).user_id.ids:
                r.can_validate = False
            else:
                if r.approval_type_id.sequential_approvals:
                    if r.env.user == r.next_approver_id:
                        r.can_validate = True
                    else:
                        r.can_validate = False
                else:
                    if r.env.user in r.request_approval_user_line_ids.user_id:
                        r.can_validate = True
                    else:
                        r.can_validate = False

    @api.depends_context('uid')
    @api.depends('state')
    def _compute_can_force_validate(self):
        is_app_admin = self.env.user.has_group('to_approvals.group_approval_manager')
        for r in self:
            if r.state in ('confirm', 'refuse') and is_app_admin:
                r.can_force_validate = True
            else:
                r.can_force_validate = False

    @api.depends_context('uid')
    @api.depends(
        'state',
        'request_approval_user_line_ids.user_id',
        'request_approval_user_line_ids.state',
        'approval_type_id.sequential_approvals')
    def _compute_can_refuse(self):
        is_app_admin = self.env.user.has_group('to_approvals.group_approval_manager')
        for r in self:
            if r.state not in ('confirm', 'validate') or r.env.user.id in r.request_approval_user_line_ids.filtered(
                lambda l: l.state == 'refused'
                ).user_id.ids:
                r.can_refuse = False
            else:
                if is_app_admin:
                    r.can_refuse = True
                else:
                    if r.approval_type_id.sequential_approvals:
                        if r.env.user == r.next_approver_id:
                            r.can_refuse = True
                        else:
                            r.can_refuse = False
                    else:
                        if r.env.user in r.request_approval_user_line_ids.filtered(lambda l: l.state not in ('approved' ,'refused')).user_id:
                            r.can_refuse = True
                        else:
                            r.can_refuse = False

    @api.depends_context('uid')
    @api.depends(
        'state',
        'employee_id.user_id',
        'request_approval_user_line_ids.user_id',
        'request_approval_user_line_ids.state',
        'approval_type_id.sequential_approvals')
    def _compute_can_mark_done(self):
        is_app_admin = self.env.user.has_group('to_approvals.group_approval_manager')
        for r in self:
            if r.state != 'validate':
                r.can_done = False
            elif is_app_admin or r._check_is_owner() or (r._check_is_manager() and r.env.user.id in r.approver_ids.ids):
                r.can_done = True
            else:
                r.can_done = False

    @api.depends_context('uid')
    @api.depends('employee_id', 'state')
    def _compute_can_cancel(self):
        is_app_admin = self.env.user.has_group('to_approvals.group_approval_manager')
        for r in self:
            if r.state != 'cancel' and is_app_admin:
                r.can_cancel = True
                continue
            if r.state in ('confirm', 'refuse') and (r._check_is_owner() or r._check_is_manager()):
                r.can_cancel = True
            else:
                r.can_cancel = False

    @api.depends_context('uid')
    @api.depends('employee_id', 'state')
    def _compute_can_draft(self):
        is_app_admin = self.env.user.has_group('to_approvals.group_approval_manager')
        for r in self:
            if r.state == 'cancel' and (is_app_admin or self._check_is_owner() or self._check_is_manager()):
                r.can_draft = True
            else:
                r.can_draft = False

    @api.constrains('request_approval_user_line_ids')
    def _check_request_approval_user_line_ids(self):
        for r in self:
            overlap_approvers = self.env['res.users']
            for request_approval_user_line in r.request_approval_user_line_ids:
                if request_approval_user_line.user_id not in overlap_approvers:
                    overlap_approvers |= request_approval_user_line.user_id
                else:
                    raise UserError(_("The user `%s` was in the approvers list already.")
                                    % request_approval_user_line.user_id.display_name)

    @api.constrains('approval_type_id', 'state')
    def _check_if_empty_lines(self):
        """
        Hook method for other extensions to inherit to check if the approval request contain empty request lines
        """
        pass

    def _check_is_owner(self):
        return self.employee_id in self.env.user.employee_ids \
            or self.env.user == self.employee_id.user_id \
            or self.env.user == self.create_uid

    def _check_is_manager(self):
        manager_users = self.employee_id._get_recursive_parents().user_id
        team_approver_rights_users = manager_users.filtered(lambda u: u.has_group('to_approvals.group_approval_team_leader'))
        return self.env.user.id in team_approver_rights_users.ids

    def _prepare_request_approval_user_line_vals_list(self):
        vals_list = []
        self.ensure_one()
        if self.employee_id and self.approval_type_id:
            # find the managers having team approval leader access rights
            managers = self.employee_id._get_recursive_parents().filtered(
                lambda emp: emp.user_id and emp.user_id.has_group('to_approvals.group_approval_team_leader')
                )
            manager_user = managers[:1].user_id
            if self.approval_type_id.manager_approval != 'none':
                # use admin if no manager found
                manager_user = manager_user or self.env.ref('base.user_admin')
                vals = {
                    'sequence': 0,
                    'user_id': manager_user.id,
                    'required': False,
                    'approval_id': self.id,
                    }
                # if manager approval is required or the manager is in the required approver list
                if self.approval_type_id.manager_approval == 'required' \
                or self.approval_type_id.type_approval_user_line_ids.filtered(
                    lambda l: l.user_id == manager_user and l.required
                    ):
                    vals['required'] = True
                vals_list.append(vals)
            # adding other approvers from the corresponding approver type
            for vals in self.approval_type_id._prepare_request_approval_user_line_vals_list():
                if self.approval_type_id.manager_approval == 'none' or vals['user_id'] != manager_user.id:
                    vals['approval_id'] = self.id
                    vals_list.append(vals)
        return vals_list

    def _get_involve_employees(self):
        """
        Hook method for others to inject or manipulated involved employees of the request
        """
        self.ensure_one()
        return self.employee_id

    def _get_next_approver(self):
        next_approve = self.request_approval_user_line_ids.filtered(
            lambda l: l.state == 'pending'
            ).sorted(lambda l: (l.sequence, l.id))[:1].user_id
        return next_approve

    def _search_my_state(self, operator, operand):
        """
        Search approval request by current user's approval status
        """
        domain = [('user_id', '=', self.env.user.id)]
        if operator in ('in', 'not in', '=', '!='):
            domain += [('state', operator, operand)]
        else:
            raise UserError(_("Operator `%s` not supported.") % operator)
        my_approval_user_lines = self.env['request.approval.user.line'].search(domain)
        return [('id', 'in', my_approval_user_lines.approval_id.ids)]

    def action_confirm(self):
        # apply `approval_action_call` in context to avoid direct state change in write()
        self = self.with_context(approval_action_call=True)
        for r in self:
            if r.state != 'draft':
                raise UserError(_("The approval request '%s' must be in Draft state in order to get confirmed.") % r.display_name)
            if not r.can_confirm:
                raise UserError(_("You might not have access right to confirm the request '%s'."
                                  " Or the request was in a status that could not get confirmed.")
                                  % r.display_name)
        if not self.request_approval_user_line_ids:
            raise UserError(_("The list of approvers for the approval request '%s'"
                              " is empty which does not make sense for an approval request."
                              " You may need to reconfigure the corresponding approval type first.")
                              % r.display_name)
        self.request_approval_user_line_ids.sudo()._to_approve()
        self.activity_update()

    def action_validate(self):
        # apply `approval_action_call` in context to avoid direct state change in write()
        self = self.with_context(approval_action_call=True)
        is_app_admin = self.user_has_groups('to_approvals.group_approval_manager')
        admin_grp = self.env.ref('to_approvals.group_approval_manager')
        force_approval = self._context.get('force_approval', False)
        if force_approval and not is_app_admin:
            raise UserError(_("Only users who are members of the group `%s` can force approval. Please contact either of"
                              " the following to get this approved anyway:\n%s")
                            % (
                                admin_grp.display_name,
                                "\n".join(admin_grp.users.mapped('name'))
                                )
                            )
        for r in self:
            if r.state not in ('confirm', 'refuse'):
                raise UserError(_("The request '%s' must be 'Confirmed' in order to get approved.") % r.display_name)
            if not r.can_validate and not r.can_force_validate:
                raise UserError(_("You do not have access right to approve the request '%s'") % r.display_name)
            if not force_approval and r.approval_type_id.sequential_approvals and r.next_approver_id:
                if r.next_approver_id != self.env.user:
                    msg = _("The request `%s` requires sequential approvals. You must wait until this get approved by %s first.") \
                        % (r.display_name, r.next_approver_id.name)
                    if r.can_force_validate:
                        msg = _("In case you want to force approval without others', please open the form view of the request and"
                                " hit the button Force Approval.")
                    raise UserError(msg)
                else:
                    for idx, line in enumerate(r.request_approval_user_line_ids):
                        if idx == 0:
                            continue
                        if line.user_id == self.env.user and (r.request_approval_user_line_ids[idx - 1].state not in ('approved', 'refused')):
                            raise UserError(_("The request `%s` requires sequential approvals while the previous approver was not take any"
                                              " action yet. You must wait until this gets either approved or refused by %s first.")
                                              % (r.display_name, r.request_approval_user_line_ids[idx - 1].user_id.name)
                                              )
            request_approval_user_lines = r.request_approval_user_line_ids.filtered(lambda x: x.user_id == self.env.user)
            if force_approval and is_app_admin:
                r.state = 'validate'
                r.forcing_approver_id = self.env.user
            elif request_approval_user_lines:
                request_approval_user_lines.sudo()._approve()
                r.activity_update()
        for r in self:
            if r.state == 'validate':
                if force_approval:
                    msg = _("The request '%s' was forced to be approved by %s whether other approvers did it or not.") \
                        % (r.display_name, self.env.user.name)
                else:
                    msg = _("The request '%s' was fully approved.") % r.display_name
                r.message_post(
                    body=msg,
                    partner_ids=(r.employee_id.user_id.partner_id | r.approver_ids.partner_id).ids
                    )

    def action_done(self):
        # apply `approval_action_call` in context to avoid direct state change in write()
        self = self.with_context(approval_action_call=True)
        for r in self:
            if r.state != 'validate':
                raise UserError(_("The request '%s' must be fully approved in order to mark as done.") % r.display_name)
            if not r.can_done:
                raise UserError(_("You may not have access right to mark the request '%s' as done.") % r.display_name)
        self.sudo().write({'state': 'done'})

    def action_refuse(self):
        # apply `approval_action_call` in context to avoid direct state change in write()
        self = self.with_context(approval_action_call=True)
        is_app_admin = self.user_has_groups('to_approvals.group_approval_manager')
        admin_grp = self.env.ref('to_approvals.group_approval_manager')
        force_approval = self._context.get('force_approval', False)
        if force_approval and not is_app_admin:
            raise UserError(_("Only users who are members of the group `%s` can force refusal. Please contact either of"
                              " the following to get this approved anyway:\n%s")
                            % (
                                admin_grp.display_name,
                                "\n".join(admin_grp.users.mapped('name'))
                                )
                            )
        for r in self:
            if r.state not in ['confirm', 'validate']:
                raise UserError(_("The request '%s' must be either 'Confirmed' or 'Approved' in order to get refused.") % r.display_name)
            if not r.can_refuse:
                raise UserError(_("You do not have access right to refuse the request '%s'") % r.display_name)
            if  not force_approval and r.approval_type_id.sequential_approvals and r.next_approver_id:
                if r.next_approver_id != self.env.user:
                    raise UserError(_("The request `%s` requires sequential approvals. You must wait until this get approved / refused by %s first.")
                                    % (r.display_name, r.next_approver_id.name)
                                    )
            request_approval_user_lines = r.request_approval_user_line_ids.filtered(lambda x: x.user_id == self.env.user)
            if request_approval_user_lines:
                request_approval_user_lines.sudo()._refuse()
                r.activity_update()
            elif force_approval and is_app_admin:
                r.state = 'refuse'

        for r in self:
            if r.state == 'refuse':
                msg = _("The request '%s' was refused.") % r.display_name
                r.message_post(
                    body=msg,
                    partner_ids=(r.employee_id.user_id.partner_id | r.approver_ids.partner_id).ids
                    )

    def action_cancel(self):
        # apply `approval_action_call` in context to avoid direct state change in write()
        self = self.with_context(approval_action_call=True)
        for r in self:
            if r.state not in ['confirm', 'validate', 'refuse', 'done']:
                raise UserError(_("The request '%s' must be in a status of either Confirmed or Approved or Refused or Done"
                                  " in order to get cancelled.") % r.display_name)
            if not r.can_cancel:
                raise UserError(_("You do not have access right to cancel the request '%s'") % r.display_name)
        self.write({'state':'cancel'})
        self.activity_update()

    def action_draft(self):
        # apply `approval_action_call` in context to avoid direct state change in write()
        self = self.with_context(approval_action_call=True)
        for r in self:
            if r.state not in ['cancel']:
                raise UserError(_("The request '%s' must be cancelled prior to getting reset to draft.") % r.display_name)
            if not r.can_draft:
                raise UserError(_("You may not have access right to reset the request '%s' to Draft") % r.display_name)
        for approver in self.request_approval_user_line_ids:
            approver.sudo()._set_to_draft()
        self.write({'state':'draft', 'forcing_approver_id': False})
        self.activity_update()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update({
                'name': self.env['ir.sequence'].next_by_code('approval.request'),
                'state': 'draft'
                })
        requests = super(ApprovalRequest, self).create(vals_list)
        requests.sudo().add_follower()
        return requests

    def write(self, vals):
        # Force using action to status control instead of direct writing state
        if 'state' in vals and not self._context.get('approval_action_call', False):
            state_change = self.filtered(lambda a: a.state != vals['state'])
            if vals['state'] == 'draft':
                state_change.action_draft()
            elif vals['state'] == 'confirm':
                state_change.action_confirm()
            elif vals['state'] == 'validate':
                state_change.action_validate()
            elif vals['state'] == 'done':
                state_change.action_done()
            elif vals['state'] == 'refuse':
                state_change.action_refuse()
            elif vals['state'] == 'cancel':
                state_change.action_cancel()
            else:
                raise ValidationError(_("Invalid status %s") % (vals['state']))
            del vals['state']
        return super(ApprovalRequest, self).write(vals)

    def unlink(self):
        for item in self:
            if item.state not in ['draft']:
                raise UserError(_("You can only delete records which are in draft status."))
        return super(ApprovalRequest, self).unlink()

    def add_follower(self):
        for r in self:
            if r.employee_id.user_id:
                r.message_subscribe(partner_ids=r.employee_id.user_id.partner_id.ids)

    def activity_update(self):
        """Schedule and Update approval activities based on current record set state."""
        to_clean = self.env['approval.request']
        to_do = self.env['approval.request']
        for r in self:

            if r.state == 'draft':
                to_clean |= r
            elif r.state == 'confirm':
                note = _("The %s request created by %s was submitted for approval") % (r.approval_type_id.name, r.create_uid.name)
                if r.approval_type_id.sequential_approvals:
                    r.sudo().activity_schedule(
                        'to_approvals.mail_act_approval',
                        note=note,
                        user_id=r.next_approver_id.id or self.env.user.id,
                        date_deadline=r.deadline
                        )
                    r.activity_feedback(['to_approvals.mail_act_approval'], r.last_approver_id.id or self.env.user.id)
                else:
                    for rpu in r.request_approval_user_line_ids.filtered(lambda l: l.state in ['pending', 'approved']):
                        if rpu.state == 'approved' and r.activity_search(['to_approvals.mail_act_approval'], rpu.user_id.id):
                            r.activity_feedback(['to_approvals.mail_act_approval'], rpu.user_id.id)
                        elif rpu.state == 'pending' and not r.activity_search(['to_approvals.mail_act_approval'], rpu.user_id.id):
                            r.sudo().activity_schedule(
                                'to_approvals.mail_act_approval',
                                note=note,
                                user_id=rpu.user_id.id or self.env.user.id,
                                date_deadline=r.deadline
                                )
            elif r.state == 'validate':
                to_do |= r
            elif r.state in ('refuse', 'cancel'):
                to_clean |= r
        if to_clean:
            to_clean.activity_unlink(['to_approvals.mail_act_approval'])
        if to_do:
            to_do.activity_feedback(['to_approvals.mail_act_approval'])

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
