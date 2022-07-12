from odoo import fields, models, api, _
from odoo.tools import groupby
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError


class HelpdeskTeam(models.Model):
    _name = 'helpdesk.team'
    _inherit = ['mail.thread', 'mail.alias.mixin', 'mail.activity.mixin', 'rating.parent.mixin']
    _description = 'Helpdesk Team'
    _order = 'sequence, name, id'
    _mail_post_access = 'read'

    name = fields.Char(string='Helpdesk Team', required=True, tracking=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide the team without removing it.")
    stage_ids = fields.Many2many('helpdesk.stage', 'helpdesk_stage_rel', 'team_id', 'stage_id', string='Stages', 
                                 help="Only contains the Stages that belong to this Team")
    ticket_ids = fields.One2many('helpdesk.ticket', 'team_id', string='Tickets',
                                 domain="[('stage_id.fold', '=', False)]", readonly=True)
    tickets_count = fields.Integer(compute='_compute_tickets_count', string="Tickets Count")
    label_tickets = fields.Char(string='Use Tickets as', default='Tickets', help="Label used for the tickets of the team.", translate=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    sequence = fields.Integer(string='Sequence')
    color = fields.Integer(string='Color Index')
    team_leader_id = fields.Many2one('res.users', string='Leader', required=True, tracking=True, check_company=True)
    team_member_ids = fields.Many2many('res.users', string='Team Member', check_company=True)
    rating_status = fields.Selection([('stage', 'Rating when changing stage'),
                                      ('periodic', 'Periodical Rating'),
                                      ('no', 'No rating')
                                      ], string='Customer Ratings', default="no", required=True,
                                      help="How to get customer feedback?\n"
                                      "- Rating when changing stage: an email will be sent when a ticket is pulled in another stage.\n"
                                      "- Periodical Rating: email will be sent periodically.\n\n"
                                      "Don't forget to set up the mail templates on the stages for which you want to get the customer's feedbacks.")
    rating_status_period = fields.Selection([('daily', 'Daily'),
                                             ('weekly', 'Weekly'),
                                             ('bimonthly', 'Twice a Month'),
                                             ('monthly', 'Once a Month'),
                                             ('quarterly', 'Quarterly'),
                                             ('yearly', 'Yearly')
                                             ], string='Rating Frequency')
    portal_show_rating = fields.Boolean(string='Rating visible publicly', copy=False, help="If True, display customer rating in Portal")
    privacy_visibility = fields.Selection([
        ('followers', 'Invited internal users'),
        ('employees', 'All internal users'),
        ('portal', 'Portal users and all internal users')
        ], string='Visibility', required=True, default='portal',
        help="Defines the visibility of the Tickets of the Team:\n"
                "- Invited internal users: Internal users may only see the followed Team and Tickets.\n"
                "- All internal users: Internal users may see All team and tickets.\n"
                "- Portal users and all internal users: Internal users may see everything.\n"
                "- Portal users may see the Team and its Tickets that followed by them or by someone in their company.")
    high_priority_tickets_count = fields.Integer(string="Number of Ticket in High Priority", compute='_compute_tickets_count')
    low_priority_tickets_count = fields.Integer(string="Number of Ticket in Low Priority", compute='_compute_tickets_count')
    urge_priority_tickets_count = fields.Integer(string="Number of Ticket in Urgent Priority", compute='_compute_tickets_count')
    alias_id = fields.Many2one('mail.alias', string='Alias', ondelete="restrict", required=True,
                               help="Internal email associated with this team. Incoming emails are automatically synchronized with Tickets.")
    assign_type = fields.Selection([
        ('random','Random'),
        ('balanced','Balanced'),
        ('manually','Manually')],
        string='Assignment Type', default='manually', required=True, copy=False,
        help="Automatic assignment type for new tickets:\n"
                "- Random: The members of the team will be assigned the same number of tickets.\n"
                "- Balanced: The new ticket will be assigned to the member with the smallest number of open tickets.\n"
                "- Manually: The new ticket will be assigned manually by the leader.")
    team_leader_excluded = fields.Boolean(string='Team Leader Excluded', default=True, copy=False,
        help="If checked, team leader will be excluded when using automatic assignment for new tickets")
    sla_ids = fields.One2many('helpdesk.sla', 'team_id', string='SLA Policies')
    apply_sla = fields.Boolean(string='Apply SLA Policies', compute='_compute_apply_sla', store=True, copy=False)
    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Hours',
        default=lambda self: self.env.company.resource_calendar_id, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    sla_count = fields.Integer(string="SLA Count" , compute='_compute_sla_count')

    alias_name = fields.Char(help="The name of the email alias, e.g. 'jobs' if you want to catch emails for <jobs@example.viindoo.com>")

    _sql_constraints = [
        ('team_name_uniq',
         'unique(name,company_id)',
         "The name of team must be unique per company"),
    ]
    
    @api.depends('sla_ids')
    def _compute_sla_count(self):
        for r in self:
            r.sla_count = len(r.sla_ids)
    @api.depends('sla_ids.team_id')
    def _compute_apply_sla(self):
        for r in self:
            r.apply_sla = True if r.sla_ids else False

    @api.depends('ticket_ids')
    def _compute_tickets_count(self):
        tickets_data = self.env['helpdesk.ticket'].read_group([('team_id', 'in', self.ids), ('stage_id.fold', '=', False)], ['priority_level', 'team_id'], ['priority_level', 'team_id'], lazy=False)
        mapped_data = {}
        for td in tickets_data:
            if td['team_id'][0] in mapped_data:
                mapped_data[td['team_id'][0]].update({td['priority_level']: td['__count']})
            else:
                mapped_data.update({td['team_id'][0]: {td['priority_level']: td['__count']}})
        for r in self:
            d = mapped_data.get(r.id, {})
            r.tickets_count = sum(d.values())
            r.low_priority_tickets_count = d.get('1', 0)
            r.high_priority_tickets_count = d.get('2', 0)
            r.urge_priority_tickets_count = d.get('3', 0)

    @api.constrains('stage_ids')
    def _check_constrains_stage(self):
        final_stage = self.stage_ids.filtered(lambda stage: stage.is_final_stage)
        if len(final_stage) > 1:
            raise ValidationError(_("The stage which have type 'Is final stage' must be unique in a team !"))

    @api.model_create_multi
    def create(self, vals_list):
        default_stage = self.env.ref('viin_helpdesk.helpdesk_stage_new', raise_if_not_found=False)
        for val in vals_list:
            val.update({'team_member_ids': [(4, val.get('team_leader_id'), 0)]})
            if default_stage and (not val.get('stage_ids', []) or not val['stage_ids'][0][2]):
                val.update({'stage_ids': [(4, default_stage.id, 0)]})
        res = super(HelpdeskTeam, self).create(vals_list)
        return res

    def write(self, vals):
        team_leader_id = vals.get('team_leader_id', False)
        if team_leader_id:
            vals.update({'team_member_ids': (vals.get('team_member_ids') or []) + [(4, team_leader_id, 0)]})
        res = super(HelpdeskTeam, self).write(vals)
        if vals.get('assign_type', False) in ('random', 'balanced'):
            tickets = self.sudo().ticket_ids.filtered(lambda r: not r.user_id)
            for ticket in tickets:
                ticket.write({'user_id': ticket.team_id._get_user_to_assign()})
        return res

    def unlink(self):
        for r in self:
            if r.ticket_ids:
                raise UserError(_("You cannot delete a Team containing Tickets or first you can delete all of its Tickets."))
        return super(HelpdeskTeam, self).unlink()

    def action_view_all_rating(self):
        """ return the action to see all the rating of the Team, and activate default filters """
        self.ensure_one()
        if self.portal_show_rating:
            return {
                'type': 'ir.actions.act_url',
                'name': "Redirect to the Website Helpdesk Team Rating Page",
                'target': 'self',
                'url': "/team/rating/%s" % (self.id,)
            }
        action = self.env['ir.actions.act_window'].for_xml_id('viin_helpdesk', 'rating_rating_action_view_team')
        action['name'] = _('Ratings of %s') % (self.name,)
        action_context = safe_eval(action['context']) if action['context'] else {}
        action_context.update(self._context)
        action_context['search_default_parent_res_name'] = self.name
        action_context.pop('group_by', None)
        return dict(action, context=action_context)

    def action_open_tickets(self):
        self.ensure_one()
        
        ctx = dict(self.env.context or {})
        ctx.update({
            'search_default_team_id': self.id,
            'default_team_id': self.id,
            })
        
        return {
            'name': _('Tickets'),
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,pivot,calendar,graph',
            'res_model': 'helpdesk.ticket',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('id', 'in', self.ticket_ids.ids)],
        }

    def action_create_new(self):
        ctx = self._context.copy()
        ctx['default_team_id'] = self.id
        return {
            'name': _('Create Ticket'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'view_id': self.env.ref('viin_helpdesk.helpdesk_ticket_form_view').id,
            'context': ctx,
        }

    def action_open_sla(self):
        self.ensure_one()
        
        ctx = dict(self.env.context or {})
        ctx.update({
            'search_default_team_id': self.id,
            'default_team_id': self.id,
            })

        return {
            'name': _('SLA Policy'),
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.sla',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('team_id', '=', self.id)],
        }

    @api.model
    def get_description_of_team(self, team_id):
        return self.browse(team_id).sudo().read(['description'])

    def get_alias_model_name(self, vals):
        return vals.get('alias_model', 'helpdesk.ticket')

    def get_alias_values(self):
        values = super(HelpdeskTeam, self).get_alias_values()
        values['alias_defaults'] = {'team_id': self.id}
        return values

    def _get_user_to_assign(self):
        """
        Get a res_users id to assign for new ticket
        :return: res_users id
        """
        self.ensure_one()
        team_member_ids = self.team_member_ids
        if not team_member_ids or self.assign_type == 'manually':
            return False
        if self.team_leader_excluded:
            team_member_ids -= self.team_leader_id
        team_member_list_ids = sorted(team_member_ids.ids)
        ticket_domain = [('team_id', '=', self.id), ('user_id', 'in', team_member_list_ids),
                         ('stage_id.fold', '=', False), ('stage_id.is_final_stage', '=', False)]
        user = self.env['res.users'].browse()
        if self.assign_type == 'balanced':
            ticket_groupby_assigned = self.env['helpdesk.ticket'].read_group(ticket_domain, ['user_id'], ['user_id'])
            # assigned_data like {user_id: user_id_count, ...}
            if ticket_groupby_assigned:
                assigned_data = dict.fromkeys(team_member_list_ids, 0)
                for value in ticket_groupby_assigned:
                    assigned_data[value['user_id'][0]] = value['user_id_count']
                # get member with the least amount of tickets
                user = user.browse(min(assigned_data, key=assigned_data.get))
        if self.assign_type == 'random':
            last_assigned_user = self.ticket_ids.sorted('id', reverse=True)[:1].user_id
            if last_assigned_user.id in team_member_list_ids:
                last_user_index = team_member_list_ids.index(last_assigned_user.id)
                # find next user to assign
                user_id = team_member_list_ids[(last_user_index + 1) % len(team_member_list_ids)]
                user = user.browse(user_id).exists()
        return user.id or team_member_ids[:1].id
