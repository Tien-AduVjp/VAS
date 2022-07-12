from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError


class MrpEco(models.Model):
    _name = 'mrp.eco'
    _description = 'Engineering Change Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', copy=False, required=True)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    type_id = fields.Many2one('mrp.eco.type', string='Type', required=True)
    stage_id = fields.Many2one('mrp.eco.stage', string='Stage', copy=False, group_expand='_read_group_stage_ids')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    tag_ids = fields.Many2many('mrp.eco.tag', string='Tags')
    priority = fields.Selection(selection=[('0', 'All'),
                                           ('1', 'Low Priority'),
                                           ('2', 'High Priority'),
                                           ('3', 'Urgent')],
                                string='Priority', default='1', index=True)
    note = fields.Text(string='Note')
    effectivity = fields.Selection([
        ('asap', 'As soon as possible'),
        ('date', 'At Date')], string='Effectivity', default='asap', required=True)
    effectivity_date = fields.Datetime(string='Effectivity Date')
    approval_ids = fields.One2many('mrp.eco.approval', 'eco_id', 'Approvals')
    state = fields.Selection([
        ('confirmed', 'To Do'),
        ('progress', 'In Progress'),
        ('done', 'Done')], string='Status', copy=False, default='confirmed', readonly=True, required=True)
    user_can_approve = fields.Boolean(string='Can Approve', compute='_compute_user_can_approve',
        help='A technical field to check if approval is required by current user')
    user_can_reject = fields.Boolean(string='Can Reject', compute='_compute_user_can_reject',
        help='A technical field to check if reject is possible by current user')
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Approved'),
        ('blocked', 'Blocked')], string='Kanban State', copy=False, compute='_compute_kanban_state', store=True)
    allow_change_stage = fields.Boolean(string='Allow Change Stage', compute='_compute_allow_change_stage')
    allow_apply_change = fields.Boolean(string='Show Apply Change', compute='_compute_allow_apply_change')
    product_tmpl_id = fields.Many2one('product.template', "Product")
    type = fields.Selection([
        ('bom', 'Bill of Materials'),
        ('routing', 'Routing'),
        ('both', 'BoM and Routing')], string='Apply on', default='bom', required=True)
    bom_id = fields.Many2one('mrp.bom', string="Bill of Materials", domain="[('product_tmpl_id', '=', product_tmpl_id)]")
    new_bom_id = fields.Many2one('mrp.bom', string='New Bill of Materials', copy=False)
    new_bom_revision = fields.Integer(string='BoM Revision', related='new_bom_id.version', store=True)
    routing_id = fields.Many2one('mrp.routing', string="Routing")
    new_routing_id = fields.Many2one('mrp.routing', string='New Routing', copy=False)
    new_routing_revision = fields.Integer(string='Routing Revision', related='new_routing_id.version', store=True)
    bom_change_ids = fields.One2many('mrp.eco.bom.change', 'eco_id', string="ECO BoM Changes", 
                                    compute='_compute_bom_change_ids', store=True)
    routing_change_ids = fields.One2many('mrp.eco.routing.change', 'eco_id', string="ECO Routing Changes", 
                                    compute='_compute_routing_change_ids', store=True)

    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Attachments',
                                    auto_join=True, domain=lambda self: [('res_model', '=', self._name)])
    # In the domain of displayed_image_id, we couln't use attachment_ids because a one2many is represented as a list of commands so we used res_model & res_id
    displayed_image_id = fields.Many2one('ir.attachment', string='Displayed Image',
                                    domain="[('res_model', '=', 'mrp.eco'), ('res_id', '=', id), ('mimetype', 'ilike', 'image')]")
    color = fields.Integer(string='Color')

    @api.depends('bom_id.bom_line_ids', 'new_bom_id.bom_line_ids')
    def _compute_bom_change_ids(self):
        for r in self:
            new_bom_commands = []
            old_bom_lines = dict(((line.product_id, line.product_uom_id,), line) for line in r.bom_id.bom_line_ids)
            if r.new_bom_id and r.bom_id:
                for line in r.new_bom_id.bom_line_ids:
                    key = (line.product_id, line.product_uom_id,)
                    old_line = old_bom_lines.pop(key, None)
                    if old_line and tools.float_compare(old_line.product_qty, line.product_qty, line.product_uom_id.rounding) != 0:
                        new_bom_commands += [(0, 0, {
                            'change_type': 'update',
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom_id.id,
                            'new_product_qty': line.product_qty,
                            'old_product_qty': old_line.product_qty})]
                    elif not old_line:
                        new_bom_commands += [(0, 0, {
                            'change_type': 'add',
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom_id.id,
                            'new_product_qty': line.product_qty
                        })]
                for key, old_line in old_bom_lines.items():
                    new_bom_commands += [(0, 0, {
                        'change_type': 'remove',
                        'product_id': old_line.product_id.id,
                        'product_uom_id': old_line.product_uom_id.id,
                        'old_product_qty': old_line.product_qty,
                    })]
            r.bom_change_ids = new_bom_commands

    @api.depends('routing_id.operation_ids', 'new_routing_id.operation_ids')
    def _compute_routing_change_ids(self):
        for r in self:
            # @TODO: should we add workcenter logic ?
            new_routing_commands = []
            old_routing_lines = dict(((op.workcenter_id,), op) for op in r.routing_id.operation_ids)
            if r.new_routing_id and r.routing_id:
                for operation in r.new_routing_id.operation_ids:
                    key = (operation.workcenter_id,)
                    old_op = old_routing_lines.pop(key, None)
                    if old_op and tools.float_compare(old_op.time_cycle_manual, operation.time_cycle_manual, 2) != 0:
                        new_routing_commands += [(0, 0, {
                            'change_type': 'update',
                            'workcenter_id': operation.workcenter_id.id,
                            'new_time_cycle_manual': operation.time_cycle_manual,
                            'old_time_cycle_manual': old_op.time_cycle_manual
                        })]
                    elif not old_op:
                        new_routing_commands += [(0, 0, {
                            'change_type': 'add',
                            'workcenter_id': operation.workcenter_id.id,
                            'new_time_cycle_manual': operation.time_cycle_manual
                        })]
                for key, old_op in old_routing_lines.items():
                    new_routing_commands += [(0, 0, {
                        'change_type': 'remove',
                        'workcenter_id': old_op.workcenter_id.id,
                        'old_time_cycle_manual': old_op.time_cycle_manual
                    })]
            r.routing_change_ids = new_routing_commands

    @api.depends('stage_id', 'approval_ids')
    def _compute_user_can_approve(self):
        approvals = self.env['mrp.eco.approval'].search([
            ('eco_id', 'in', self.ids),
            ('status', 'not in', ['approved']),
            ('template_stage_id', 'in', self.stage_id.ids),
            ('approval_template_id.approval_type', 'in', ('mandatory', 'optional')),
            ('required_user_ids', 'in', self.env.uid)])
        to_approve_eco_ids = approvals.eco_id.ids
        for r in self:
            r.user_can_approve = r.id in to_approve_eco_ids

    @api.depends('stage_id', 'approval_ids')
    def _compute_user_can_reject(self):
        approvals = self.env['mrp.eco.approval'].search([
            ('eco_id', 'in', self.ids),
            ('status', 'not in', ['rejected']),
            ('template_stage_id', 'in', self.stage_id.ids),
            ('approval_template_id.approval_type', 'in', ('mandatory', 'optional')),
            ('required_user_ids', 'in', self.env.uid)])
        to_reject_eco_ids = approvals.eco_id.ids
        for r in self:
            r.user_can_reject = r.id in to_reject_eco_ids

    @api.depends('approval_ids.is_approved', 'approval_ids.is_rejected', 'approval_ids.template_stage_id')
    def _compute_kanban_state(self):
        """ State of ECO is based on the state of approvals for the current stage. """
        for r in self:
            approvals = r.approval_ids.filtered(lambda app: app.template_stage_id == r.stage_id)
            if not approvals:
                r.kanban_state = 'normal'
            elif all(approval.is_approved for approval in approvals):
                r.kanban_state = 'done'
            elif any(approval.is_rejected for approval in approvals):
                r.kanban_state = 'blocked'
            else:
                r.kanban_state = 'normal'

    @api.depends('kanban_state', 'stage_id', 'approval_ids.template_stage_id')
    def _compute_allow_change_stage(self):
        for r in self:
            approvals = r.approval_ids.filtered(lambda app: app.template_stage_id == r.stage_id)
            if approvals:
                r.allow_change_stage = r.kanban_state == 'done'
            else:
                r.allow_change_stage = r.kanban_state in ['normal', 'done']

    @api.depends('state', 'stage_id.is_final_stage')
    def _compute_allow_apply_change(self):
        for r in self:
            r.allow_apply_change = r.stage_id.is_final_stage and r.state in ('confirmed', 'progress')

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.product_tmpl_id.bom_ids:
            self.bom_id = self.product_tmpl_id.bom_ids.ids[0]

    @api.onchange('bom_id', 'type')
    def onchange_bom_id(self):
        if self.type == 'both':
            self.routing_id = self.bom_id.routing_id

    @api.model
    def create(self, vals):
        prefix = self.env['ir.sequence'].next_by_code('mrp.eco') or ''
        vals['name'] = '%s%s' % (prefix and '%s: ' % prefix or '', vals.get('name', ''))
        
        type_id = vals.get('type_id', False)
        if type_id and not vals.get('stage_id', False):
            stage = self.env['mrp.eco.stage'].search([('type_ids', '=', type_id)], limit=1)
            if stage:
                vals.update({'stage_id': stage.id})
        
        eco = super(MrpEco, self).create(vals)
        eco._create_approvals()
        return eco

    def write(self, vals):
        stage_id = vals.get('stage_id')
        if stage_id:
            new_stage = self.env['mrp.eco.stage'].browse(stage_id)
            for r in self.filtered(lambda r: r.stage_id):
                if not r.allow_change_stage:
                    raise UserError(_("You cannot change the stage on the ECO '%s', as approvals are still required.") % r.name)
                has_blocking_stages = self.env['mrp.eco.stage'].search_count([
                    ('sequence', '>=', r.stage_id.sequence),
                    ('sequence', '<=', new_stage.sequence),
                    ('type_ids', '=', r.type_id.id),
                    ('id', 'not in', [r.stage_id.id, vals['stage_id']]),
                    ('is_blocking', '=', True)])
                if has_blocking_stages:
                    raise UserError(_("You cannot change the stage on the ECO '%s', as approvals are required in the process.") % r.name)
                if r.state == 'done' and not new_stage.is_final_stage:
                    raise UserError(_("You cannot change the stage on a applied ECO '%s'.") % r.name)
            
        res = super(MrpEco, self).write(vals)
        if stage_id:
            self._create_approvals()
        return res

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = []
        if self._context.get('default_type_id'):
            search_domain = [('type_ids', '=', self._context['default_type_id'])]
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.returns('self', lambda value: value.id)
    def message_post(self, **kwargs):
        message = super(MrpEco, self).message_post(**kwargs)
        if message.message_type == 'comment' and message.author_id == self.env.user.partner_id:
            for r in self:
                approvals = r.approval_ids.filtered(lambda app: app.template_stage_id == self.stage_id and app.status == 'none')
                datas = self.env['mrp.eco.approval']
                for approval in approvals:
                    if self.env.user in approval.approval_template_id.user_ids:
                        datas += approval
                if datas:
                    datas.write({
                            'status': 'comment',
                            'user_id': self.env.uid
                        })
        return message

    def _create_approvals(self):
        for r in self:
            datas = []
            for approval_template in r.stage_id.approval_template_ids:
                datas.append({
                        'eco_id': r.id,
                        'approval_template_id': approval_template.id,
                    })
            if datas:
                self.env['mrp.eco.approval'].create(datas)

    def action_approve(self):
        for r in self:
            approvals = r.approval_ids.filtered(lambda a: a.template_stage_id == self.stage_id and a.approval_template_id.approval_type in ('mandatory', 'optional'))
            datas = self.env['mrp.eco.approval']
            for approval in approvals:
                if self.env.user in approval.approval_template_id.user_ids:
                    datas += approval
            if datas:
                datas.write({
                    'status': 'approved',
                    'user_id': self.env.uid
                })

    def action_reject(self):
        for r in self:
            approvals = r.approval_ids.filtered(lambda a: a.template_stage_id == self.stage_id and a.approval_template_id.approval_type in ('mandatory', 'optional'))
            datas = self.env['mrp.eco.approval']
            for approval in approvals:
                if self.env.user in approval.approval_template_id.user_ids:
                    datas += approval
            if datas:
                datas.write({
                    'status': 'rejected',
                    'user_id': self.env.uid
                })

    def action_new_revision(self):
        for r in self:
            if r.type in ('bom', 'both'):
                r.new_bom_id = r.bom_id.copy(default={
                    'version': r.bom_id.version + 1,
                    'active': False,
                    'previous_bom_id': r.bom_id.id,
                }).id
            if r.type in ('routing', 'both'):
                r.new_routing_id = r.routing_id.copy(default={
                    'version': r.routing_id.version + 1,
                    'active': False,
                    'previous_routing_id': r.routing_id.id
                }).id
            if r.type == 'both':
                r.new_bom_id.routing_id = r.new_routing_id.id
                for line in r.new_bom_id.bom_line_ids:
                    line.operation_id = r.new_routing_id.operation_ids.filtered(lambda x: x.name == line.operation_id.name).id
        self.write({'state': 'progress'})

    def action_apply(self):
        self.new_bom_id._action_apply_new_version()
        self.new_routing_id._action_apply_new_version()
        self.write({'state': 'done'})

    def open_new_bom(self):
        self.ensure_one()
        return {
            'name': _('Eco BoM'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.new_bom_id.id}

    def open_new_routing(self):
        self.ensure_one()
        return {
            'name': _('Eco Routing'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.routing',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.new_routing_id.id}
