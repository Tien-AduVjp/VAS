from odoo import models, fields, api
from ast import literal_eval


class ApprovalRequestType(models.Model):
    _name = 'approval.request.type'
    _description = "Approval Request Type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'

    name = fields.Char(string="Title", required=True)
    type = fields.Selection([('generic', 'Generic')], string="Type", required=True, default='generic')
    validation_type = fields.Selection([
        ('no_validation', 'No Validation'),
        ('hr', 'Approval Officer'),
        ('leader', 'Manager'),
        ('both', 'Manager and Approval Officer')], default='both', required=True, string='Validation',
        help="How the requests of this type is approved.\n"
        "* No Validation: all the requests of this type will be approved automatically upon confirmation;\n"
        "* Approval Officer: all the requests of this type will be required to get approved by a user specified"
        " in the field 'Responsible' below;\n"
        "* Manager: all the requests of this type will be required to get approved by a superior of the employee's"
        " (including all the superior and the manager of the employee's department, excluding himself);\n"
        "* Manager and Approval Officer: this will trigger 2-step approval process for all the requests"
        " of this type. The first approval will be done by a manager or any superior of the employee's"
        " and the second approval will be done by the one specified in the field 'Responsible' below.")
    responsible_id = fields.Many2one('res.users', 'Responsible', tracking=True,
        domain=lambda self: [('groups_id', 'in', [self.env.ref('to_approvals.group_approval_officer').id])],
        help="This user will be responsible for approving or validating this type of approval")
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    requests_count = fields.Integer(string='Requests Count', compute='_compute_requests_count')
    waiting_requests_count = fields.Integer(string='Waiting Requests', compute='_compute_requests_count')
    approved_requests_count = fields.Integer(string='Approved Requests', compute='_compute_requests_count')
    request_ids = fields.One2many('approval.request', 'approval_type_id', string='Approval Request', readonly=True)
    
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
            if d['state'] in ('confirm', 'validate1'):
                mapped_data[approval_type_id]['waiting_requests_count'] += d.get('__count', 0)
            elif d['state'] == 'validate':
                mapped_data[approval_type_id]['approved_requests_count'] += d.get('__count', 0)
            
        for record in self:
            d = mapped_data.get(record.id, {})
            record.approved_requests_count = d.get('approved_requests_count', 0)
            record.requests_count = d.get('requests_count', 0)
            record.waiting_requests_count = d.get('waiting_requests_count', 0)
    
    @api.onchange('validation_type')
    def _onchange_responsible_id(self):
        for r in self:
            if r.validation_type in ['no_validation', 'leader']:
                r.responsible_id = False

    def _get_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).read()[0]
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
        action = self.env.ref('to_approvals.action_approval_request_tree_waiting')
        result = action.read()[0]
        # override to get rid off the default context
        if len(self) == 1:
            result['context'] = {
                'default_approval_type_id': self.id,
                'default_company_id': self.company_id.id
                }
        elif len(self) > 1:
            result['context'] = {
                'default_approval_type_id': self[0].id,
                'default_company_id': self[0].company_id.id
                }
        else:
            result['context'] = {}
        # choose view mode
        requests = self.mapped('request_ids')
        if len(requests) != 1:
            result['domain'] = [('approval_type_id', 'in', self.ids)]
        elif len(requests) == 1:
            res = self.env.ref('to_approvals.approval_request_view_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = requests.id
        return result

    def action_view_approved_requests(self):
        self.ensure_one()
        action = self.env.ref('to_approvals.action_approval_request_tree_waiting')
        result = action.read()[0]
        # override to get rid off the default context
        result['context'] = {
            'default_approval_type_id': self.id,
            'default_company_id': self.company_id.id
            }
        # choose view mode
        requests = self.mapped('request_ids').filtered(lambda x: x.state == 'validate')
        if len(requests) != 1:
            result['domain'] = [('state', '=', 'validate'), ('approval_type_id', '=', self.id)]
        elif len(requests) == 1:
            res = self.env.ref('to_approvals.approval_request_view_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = requests.id
        return result

    def action_view_waiting_requests(self):
        self.ensure_one()
        action = self.env.ref('to_approvals.action_approval_request_tree_waiting')
        result = action.read()[0]
        # override to get rid off the default context
        result['context'] = {
            'default_approval_type_id': self.id,
            'default_company_id': self.company_id.id
            }
        # choose view mode
        requests = self.mapped('request_ids').filtered(lambda x: x.state in ('confirm', 'validate1'))
        if len(requests) != 1:
            result['domain'] = [('state', 'in', ('confirm', 'validate1')), ('approval_type_id', '=', self.id)]
        elif len(requests) == 1:
            res = self.env.ref('to_approvals.approval_request_view_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = requests.id
        return result

    def get_approval_request_form_views(self):
        context = self._context.copy()
        context['default_approval_type_id'] = self.id
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
