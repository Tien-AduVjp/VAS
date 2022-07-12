from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import format_date


class TeamSalesTarget(models.Model):
    _name = 'team.sales.target'
    _inherit = 'abstract.sales.target'
    _description = 'Team Sales Target'
    _rec_name = 'crm_team_id'

    crm_team_id = fields.Many2one('crm.team', string='Sales Team', required=True, index=True,
                                  readonly=False, states={'confirmed': [('readonly', True)],
                                                          'refused': [('readonly', True)],
                                                          'approved': [('readonly', True)],
                                                          'cancelled': [('readonly', True)]})

    personal_target_ids = fields.One2many('personal.sales.target', 'team_target_id', string='Personal Sales Targets',
                                          help="Sales targets for the team members which will be suggested automatically on changing the Sales Team."
                                          " Please remember to add member to the team first to have the targets suggested.",
                                          readonly=False, states={'confirmed': [('readonly', True)],
                                                                  'refused': [('readonly', True)],
                                                                  'approved': [('readonly', True)],
                                                                  'cancelled': [('readonly', True)]}, compute="_compute_personal_target_ids", store=True)

    @api.constrains('start_date', 'end_date', 'crm_team_id')
    def _check_overlapping(self):
        TeamTarget = self.env['team.sales.target']
        for r in self:
            overlap = TeamTarget.search([('crm_team_id', '=', r.crm_team_id.id), ('id', '!=', r.id),
                                         ('start_date', '<=', r.end_date),
                                         ('end_date', '>=', r.start_date)], limit=1)
            if overlap:
                raise ValidationError(_("The target you've input is overlapping an existing one which has Date Start: %s, Date End: %s")
                                      % (overlap.start_date, overlap.end_date))

    def _prepare_personal_target_data(self, user, target):
        return {
            'sale_person_id': user.id,
            'team_target_id': self.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'target': target,
            'state': self.state,
            }

    @api.depends('crm_team_id','target')
    def _compute_personal_target_ids(self):
        for r in self:        
            if r.crm_team_id:
            # compute personal target by equal dividing
                if not r.crm_team_id.member_ids:
                    personal_target = 0.0
                else:
                    personal_target = r.target / len(r.crm_team_id.member_ids)
    
                personal_target_ids = r.env['personal.sales.target']
                for member in r.crm_team_id.member_ids:
                    # check if there is an existing line, then use it.
                    if r._origin.id > 0:
                        existing_line = personal_target_ids.search([('sale_person_id', '=', member.id), ('team_target_id', '=', r._origin.id)], limit=1)
                        if existing_line:
                            personal_target_ids += existing_line
                            continue
                    # no existing line, create a new one.
                    new_line = personal_target_ids.new(r._prepare_personal_target_data(member, personal_target))
                    personal_target_ids += new_line
                r.personal_target_ids = personal_target_ids
            else:
                r.personal_target_ids = False

    def subscribe_team_leader(self):
        for r in self:
            subscribers = []
            if r.crm_team_id:
                if r.crm_team_id.user_id and r.crm_team_id.user_id.partner_id not in r.message_follower_ids.partner_id:
                    subscribers += [r.crm_team_id.user_id.partner_id.id]
            if subscribers:
                r.message_subscribe(subscribers)

    def subscribe_approvers(self):
        for r in self:
            subscribers = []
            if r.crm_team_id:
                if r.crm_team_id.regional_manager_id and r.crm_team_id.regional_manager_id.partner_id not in r.message_follower_ids.partner_id:
                    subscribers += [r.crm_team_id.regional_manager_id.partner_id.id]
            if subscribers:
                r.message_subscribe(subscribers)

    def action_confirm(self):
        self.mapped('personal_target_ids').action_confirm()
        super(TeamSalesTarget, self).action_confirm()
        self.subscribe_approvers()

    def action_draft(self):
        self.mapped('personal_target_ids').action_draft()
        super(TeamSalesTarget, self).action_draft()

    def action_refuse(self):
        is_regional_sales_manager = self.env.user.has_group('to_sales_team_advanced.group_sale_regional_manager')
        for r in self:
            if not is_regional_sales_manager:
                raise ValidationError(_("You must be granted with Regional Sales Manager access rights"
                                        " to refuse the sales target for the sales team '%s'")
                                        % (r.crm_team_id.name,))
            if r.personal_target_ids:
                r.personal_target_ids.action_refuse()
        super(TeamSalesTarget, self).action_refuse()

    def action_approve(self):
        is_regional_sales_manager = self.env.user.has_group('to_sales_team_advanced.group_sale_regional_manager')
        for r in self:
            if not is_regional_sales_manager:
                raise ValidationError(_("You must be granted with Regional Sales Manager access rights"
                                        " to approve the sales target for the sales team '%s'")
                                        % (r.crm_team_id.name,))
            if r.personal_target_ids:
                r.personal_target_ids.action_approve()
        super(TeamSalesTarget, self).action_approve()

    def action_cancel(self):
        is_regional_sales_manager = self.env.user.has_group('to_sales_team_advanced.group_sale_regional_manager')
        for r in self:
            if not is_regional_sales_manager and r.state == 'approved':
                raise ValidationError(_("You must be granted with Regional Sales Manager access rights"
                                        " to cancel the approved sales target for the sales team '%s'")
                                        % (r.crm_team_id.name,))
        self.mapped('personal_target_ids').action_cancel()
        super(TeamSalesTarget, self).action_cancel()

    @api.model_create_multi
    def create(self, vals_list):
        records = super(TeamSalesTarget, self).create(vals_list)
        records.subscribe_team_leader()
        return records

    def write(self, vals):
        if 'crm_team_id' in vals:
            for r in self:
                unsubscribers = []
                if r.crm_team_id.user_id:
                    unsubscribers += [r.crm_team_id.user_id.partner_id.id]

                if unsubscribers:
                    r.message_unsubscribe(unsubscribers)
        res = super(TeamSalesTarget, self).write(vals)
        if 'crm_team_id' in vals:
            self.subscribe_team_leader()
        return res

    def _build_name(self):
        return "%s [%s] [%s ~ %s]" % (self.crm_team_id.name, self.target, format_date(self.env, self.start_date), format_date(self.env, self.end_date))

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, r._build_name()))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('crm_team_id.name', 'ilike', name + '%'), ('name', operator, name)]
        tags = self.search(domain + args, limit=limit)
        return tags.name_get()
    
