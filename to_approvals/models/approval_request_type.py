from ast import literal_eval

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import relativedelta



class ApprovalRequestType(models.Model):
    _name = 'approval.request.type'
    _description = "Approval Request Type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'

    name = fields.Char(string='Title', required=True, tracking=True)
    type = fields.Selection([('generic', 'Generic')], string='Type', required=True, default='generic', tracking=True)
    type_approval_user_line_ids = fields.One2many('type.approval.user.line', 'request_type_id', string='Type Approvers',
                                                  help="Specify approvers for requests of this type.")
    approver_ids = fields.Many2many('res.users', 'approval_request_type_res_users_rel', 'approval_request_type_id', 'user_id',
                                    string='Approvers', compute='_compute_approvers', store=True)
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company, tracking=True)
    requests_count = fields.Integer(string='Requests Count', compute='_compute_requests_count')
    waiting_requests_count = fields.Integer(string='Waiting Requests', compute='_compute_requests_count')
    approved_requests_count = fields.Integer(string='Approved Requests', compute='_compute_requests_count')
    request_ids = fields.One2many('approval.request', 'approval_type_id', string='Approval Request', readonly=True)
    manager_approval = fields.Selection([
        ('none', 'None'),
        ('optional', 'Optional'),
        ('required', 'Required'),
        ], string='Employee\'s Manager Required', required=True, default='required', tracking=True,
        help="Control how the manager of the employee gets involved in approval process of the requests of this type.\n"
        "* None: The manager will not involve.\n"
        "* Optional: The manager will be one of the approvers but he is not required to approve; The request still can get"
        " approved if all the required approvers approve it and the minimum approvals condition is met.\n"
        "* Required: The manager will be one of the required approvers of the request. It means that the request will not be able"
        " to get approved without the manager's approval.\n"
        "NOTE: An employee manager here mentioned here is a user who belongs to the group `Team Approver` and links to"
        " an employee that is either direct or indirect manager of the current employee. A manager that is not a member of"
        " Team Approver will not be able to approve requests.")
    mimimum_approvals = fields.Integer(string='Minimum Approvals', compute='_compute_mimimum_approvals', store=True, readonly=False,
                                       required=True, tracking=True, default=1)
    mimimum_approvals_exceed_warning = fields.Char(string='Minimum Approvals Exceed Warning', translate=True,
                                                   compute='_compute_mimimum_approvals_exceed_warning')
    sequential_approvals = fields.Boolean(string='Sequential Approvals', default=False, tracking=True,
                                                help="If enabled, approvers will be suggested to approve the requests of this type sequentially.")
    days_to_approve = fields.Integer(string='Days to Approve', default=1, required=True, tracking=True,
                                     help="The required number of days for approvers to approve the requests of this type."
                                     " In other words, this number will be used to calculate approval deadline for the requests"
                                     " of this type.")

    _sql_constraints = [
        ('mimimum_approvals_check', "CHECK (mimimum_approvals > 0)", "Minimum approvals must be greater than zero"),
        ('days_to_approve_check', "CHECK (days_to_approve >= 0)", "Days to approve must be greater than or equal to zero")
    ]

    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        default = dict(
            default or {},
            type_approval_user_line_ids=self.type_approval_user_line_ids,
        )
        return super(ApprovalRequestType, self).copy(default=default)

    def _compute_requests_count(self):
        data = self.env['approval.request'].read_group(
            [('approval_type_id', 'in', self.ids)],
            ['approval_type_id', 'state'],
            ['approval_type_id', 'state'],
            lazy=False
            )
        mapped_data = {}
        for d in data:
            approval_type_id = d['approval_type_id'][0]
            if approval_type_id not in mapped_data:
                mapped_data[approval_type_id] = {
                    'requests_count': 0,
                    'waiting_requests_count': 0,
                    'approved_requests_count': 0,
                    }
            mapped_data[approval_type_id]['requests_count'] += d.get('__count', 0)
            if d['state'] == 'confirm':
                mapped_data[approval_type_id]['waiting_requests_count'] += d.get('__count', 0)
            elif d['state'] == 'validate':
                mapped_data[approval_type_id]['approved_requests_count'] += d.get('__count', 0)

        for record in self:
            d = mapped_data.get(record.id, {})
            record.approved_requests_count = d.get('approved_requests_count', 0)
            record.requests_count = d.get('requests_count', 0)
            record.waiting_requests_count = d.get('waiting_requests_count', 0)

    @api.depends('type_approval_user_line_ids.user_id')
    def _compute_approvers(self):
        for r in self:
            r.approver_ids = r.type_approval_user_line_ids.user_id

    @api.depends('manager_approval', 'type_approval_user_line_ids.required')
    def _compute_mimimum_approvals(self):
        for r in self:
            r.mimimum_approvals = r._count_required_appovers()

    @api.depends('mimimum_approvals', 'approver_ids', 'manager_approval')
    def _compute_mimimum_approvals_exceed_warning(self):
        mimimum_approvals_exceed_warning = _(
            "Your minimum approval exceeds the total of default approvers."
            " Please either reduce the Minimum Approvals or add more approvers."
            )
        for r in self:
            approvals = 1 if r.manager_approval != 'none' else 0
            approvals += len(r.approver_ids)
            r.mimimum_approvals_exceed_warning = mimimum_approvals_exceed_warning if r.mimimum_approvals > approvals else False

    @api.constrains('type_approval_user_line_ids')
    def _check_type_approval_user_line_ids(self):
        for r in self:
            overlap_approvers = self.env['res.users']
            for type_approval_user_line in r.type_approval_user_line_ids:
                if type_approval_user_line.user_id not in overlap_approvers:
                    overlap_approvers |= type_approval_user_line.user_id
                else:
                    raise UserError(_("The user `%s` was in the approvers list already.") % type_approval_user_line.user_id.display_name)

    @api.constrains('mimimum_approvals', 'type_approval_user_line_ids', 'manager_approval')
    def _check_mimimum_approvals(self):
        for r in self:
            if r.mimimum_approvals < r._count_required_appovers():
                raise UserError(_("Minimum approvals must be greater than or equal to the total number of required approvers."))

    def _prepare_request_approval_user_line_vals_list(self):
        self.ensure_one()
        vals_list = []
        for type_approval_user_line in self.type_approval_user_line_ids.filtered(
            lambda l: l.user_id and l.user_id.has_group('to_approvals.group_approval_officer')
            ):
            vals_list.append(type_approval_user_line._prepare_request_approval_user_line_vals())
        return vals_list

    def _count_required_appovers(self):
        manager_approval = 1 if self.manager_approval == 'required' else 0
        return len(self.type_approval_user_line_ids.filtered(lambda tau: tau.required)) + manager_approval

    def _get_action(self, action_xmlid):
        action = self.env['ir.actions.act_window']._for_xml_id(action_xmlid)
        if self:
            action['display_name'] = self.display_name

        context = {
            'search_default_approval_type_id': [self.id],
            'default_approval_type_id': self.id,
            'default_company_id': self.company_id.id,
        }

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        return action

    def get_action_approval_request_type(self):
        return self._get_action('to_approvals.approval_request_action')

    def action_view_requests(self):
        action = self.env['ir.actions.act_window']._for_xml_id('to_approvals.action_approval_request_tree_waiting')
        # override to get rid off the default context
        if len(self) == 1:
            action['context'] = {
                'default_approval_type_id': self.id,
                'default_company_id': self.company_id.id
                }
        elif len(self) > 1:
            action['context'] = {
                'default_approval_type_id': self[0].id,
                'default_company_id': self[0].company_id.id
                }
        else:
            action['context'] = {}
        # choose view mode
        requests = self.mapped('request_ids')
        if len(requests) != 1:
            action['domain'] = [('approval_type_id', 'in', self.ids)]
        elif len(requests) == 1:
            res = self.env.ref('to_approvals.approval_request_view_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = requests.id
        return action

    def action_view_approved_requests(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('to_approvals.action_approval_request_tree_waiting')
        # override to get rid off the default context
        action['context'] = {
            'default_approval_type_id': self.id,
            'default_company_id': self.company_id.id
            }
        # choose view mode
        requests = self.mapped('request_ids').filtered(lambda x: x.state == 'validate')
        if len(requests) != 1:
            action['domain'] = [('state', '=', 'validate'), ('approval_type_id', '=', self.id)]
        elif len(requests) == 1:
            res = self.env.ref('to_approvals.approval_request_view_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = requests.id
        return action

    def action_view_waiting_requests(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('to_approvals.action_approval_request_tree_waiting')
        # override to get rid off the default context
        action['context'] = {
            'default_approval_type_id': self.id,
            'default_company_id': self.company_id.id
            }
        # choose view mode
        requests = self.mapped('request_ids').filtered(lambda x: x.state in ('confirm', 'validate1'))
        if len(requests) != 1:
            action['domain'] = [('state', 'in', ('confirm', 'validate1')), ('approval_type_id', '=', self.id)]
        elif len(requests) == 1:
            res = self.env.ref('to_approvals.approval_request_view_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = requests.id
        return action

    def get_approval_request_form_views(self):
        context = self._context.copy()
        today = fields.Date.today()
        context['default_approval_type_id'] = self.id
        context['default_deadline'] = today + relativedelta(days=self.days_to_approve or 0)
        return {
            'name': "Approval Request",
            'res_model': "approval.request",
            'type': "ir.actions.act_window",
            'context': context,
            'view_mode': "form",
            'view_type': "form",
            'view_id': self.env.ref("to_approvals.approval_request_view_form").id,
            'target': "self"
        }

    def _get_deadline(self):
        return fields.Date.today() + relativedelta(days = self.days_to_approve or 0)
