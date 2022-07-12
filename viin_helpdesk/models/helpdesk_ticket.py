from werkzeug.urls import url_encode

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessDenied
from odoo import tools
from odoo.tools import html2plaintext
from odoo.tools.safe_eval import safe_eval

DAYS = 24 * 60 * 60


def _calculate_duration(end_date, start_date):
    duration = 0.0

    if end_date and start_date:
        delta = end_date - start_date
        if delta.days >= 0:
            duration = (delta.days * DAYS + delta.seconds) / 60 / 60
    # remove microseconds for result
    return duration


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'rating.mixin', 'portal.mixin']
    _description = 'Helpdesk Ticket'
    _order = 'priority_level asc, id desc'
    _mail_post_access = 'read'

    @api.model
    def _expand_group_stage(self, stages, domain, order):
        domain = [('id', 'in', stages.ids)]
        team_id = self.env.context.get('default_team_id', False)
        if team_id:
            domain = ['|', ('team_ids', 'in', team_id)] + domain
        return stages.search(domain, order=order)

    name = fields.Char(string='Subject', required=True, tracking=True)
    description = fields.Html(string='Description', help="Description detail of the request support by partner")
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10, string='Sequence', help="Gives the sequence order when displaying a list of Tickets.")
    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string='Ticket Type', tracking=True,
                                     help="Used to classify question type for customer")
    tag_ids = fields.Many2many('helpdesk.tag', string="Tags")
    user_id = fields.Many2one('res.users', string='Assigned To', tracking=True, copy=False,
                              domain="[('helpdesk_team_ids', '=', team_id)]", help="The responsible this ticket")
    team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team', default=lambda self: self.env.company.default_helpdesk_team_id, tracking=True, copy=False, help="Used to classify support group for customer")
    priority_level = fields.Selection([
        ('0', 'All'),
        ('1', 'Low Priority'),
        ('2', 'High Priority'),
        ('3', 'Urgent')
    ], string='Priority', tracking=True, default='0', help="Display priority level for ticket")
    partner_id = fields.Many2one('res.partner', string='Partner', help="You can choose a partner if you want them to follow this ticket.")
    email_from = fields.Char(string='Email', help="Email address of the contact", compute='_compute_email_from', readonly=False, store=True)
    email_formatted = fields.Char(string='Formatted Email', compute='_compute_email_formatted', help="Format email address 'Name <email@domain>'")
    contact_name = fields.Char(string='Contact Name')
    send_notification_email = fields.Boolean(string='Send Notification Email', default=False,
                                             help="If set, then an email will be sent to the partner when the ticket changes stage.")
    stage_id = fields.Many2one('helpdesk.stage', string='Stage', ondelete='restrict',
                               tracking=True, index=True, copy=False,
                               group_expand='_expand_group_stage',
                               domain="[('team_ids', '=', team_id)]")
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')
    ], string='Kanban State', default='normal', tracking=True)
    assign_date = fields.Datetime(string='Assign Date', compute='_compute_assign_date', store=True, tracking=True, copy=False,
                                  help="When employee has Assigned, this field will automatically set the current time")
    end_date = fields.Datetime(string='End Date', compute='_compute_end_date', store=True, tracking=True, copy=False)
    assign_duration = fields.Float(string='Assigning Duration', compute='_compute_assign_duration', store=True,
                                   help="The duration in hours counted from the date and time the ticket is created"
                                   " to the date and time it is assigned to a team member.")
    resolved_duration = fields.Float(string='Resolving Duration', compute='_compute_resolved_duration', store=True,
                                     help="The duration in hours counted from the date and time the ticket is assigned"
                                     " to the date and time it is marked as resolved.")
    ticket_life = fields.Float(string='Ticket Life', compute='_compute_ticket_life', store=True)
    color = fields.Integer(string='Color Index')
    company_id = fields.Many2one('res.company', related='team_id.company_id', string='Company', store=True)
    rating_status = fields.Selection([
        ('stage', 'Rating when changing stage'),
        ('periodic', 'Periodical Rating'),
        ('no', 'No rating')
    ], string='Customer Ratings', compute='_compute_customer_ratings', store=True, readonly=False,
                                      help="How to get customer feedback?\n"
                                      "- Rating when changing stage: an email will be sent when a ticket is pulled in another stage.\n"
                                      "- Periodical Rating: email will be sent periodically.\n\n"
                                      "Don't forget to set up the mail templates on the stages for which you want to get the customer's feedbacks.")
    rating_status_period = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('bimonthly', 'Twice a Month'),
        ('monthly', 'Once a Month'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], string='Rating Frequency', compute='_compute_customer_ratings', store=True, readonly=False)
    portal_show_rating = fields.Boolean('Rating visible publicly', copy=False, compute='_compute_customer_ratings',
                                        store=True, readonly=False, help="If True, display Customer Rating in Portal")
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True, related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True, related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label', tracking=True)
    #sla policies
    sla_ids = fields.Many2many('helpdesk.sla', 'helpdesk_ticket_sla_rel', string='SLAs', compute='_compute_sla_ids', store=True, copy=False)
    sla_line_ids = fields.One2many('helpdesk.sla.line', 'ticket_id', string='SLA Status', compute='_compute_sla_line_ids', store=True)

    @api.model
    def default_get(self, fields):
        res = super(HelpdeskTicket, self).default_get(fields)

        team_id = self.env.context.get('default_team_id', res.get('team_id', False))
        if team_id:
            team_id = self.env['helpdesk.team'].browse(team_id)
            company = team_id.company_id or self.env.company
            if 'team_id' in fields and 'team_id' not in res:
                res['team_id'] = team_id.id or company.default_helpdesk_team_id.id
            if 'stage_id' in fields and 'stage_id' not in res and team_id.stage_ids:
                res['stage_id'] = team_id.stage_ids[0].id
            if 'company_id' in fields and 'company_id' not in res:
                res['company_id'] = company.id
            if 'user_id' in fields and 'user_id' not in res:
                res['user_id'] = team_id._get_user_to_assign()
        return res

    @api.depends('partner_id')
    def _compute_email_from(self):
        for r in self:
            if r.partner_id:
                r.email_from = r.partner_id.email
            else:
                r.email_from = ''

    @api.depends('contact_name', 'email_from')
    def _compute_email_formatted(self):
        for r in self:
            if r.email_from:
                r.email_formatted = tools.formataddr((r.contact_name or u"False", r.email_from or u"False"))
            else:
                r.email_formatted = ''

    # When you change Stage to Final stage, update End Date.
    @api.depends('stage_id.fold', 'stage_id.is_final_stage')
    def _compute_end_date(self):
        for r in self:
            if r.user_id and (r.stage_id.fold or r.stage_id.is_final_stage):
                r.end_date = fields.Datetime.now()
            else:
                r.end_date = False

    @api.depends('user_id')
    def _compute_assign_date(self):
        for r in self:
            if r.user_id:
                r.assign_date = fields.Datetime.now()
            else:
                r.assign_date = False

    # Calculation the time intervals
    @api.depends('assign_date')
    def _compute_assign_duration(self):
        for r in self:
            if r.assign_date:
                r.assign_duration = _calculate_duration(r.assign_date, r.create_date)
            else:
                r.assign_duration = 0.0

    @api.depends('assign_date', 'end_date')
    def _compute_resolved_duration(self):
        for r in self:
            if r.assign_date and r.end_date:
                r.resolved_duration = _calculate_duration(r.end_date, r.assign_date)
            else:
                r.resolved_duration = 0.0

    @api.depends('end_date')
    def _compute_ticket_life(self):
        for r in self:
            if r.end_date:
                r.ticket_life = _calculate_duration(r.end_date, r.create_date)
            else:
                r.ticket_life = 0.0

    @api.depends('team_id', 'tag_ids', 'priority_level', 'ticket_type_id', 'team_id.sla_ids.minimum_priority', 'team_id.sla_ids.ticket_type_ids', 'team_id.sla_ids.tag_ids')
    def _compute_sla_ids(self):
        slas = self.team_id.sla_ids
        slas.read(['team_id', 'minimum_priority', 'ticket_type_ids', 'tag_ids'])
        for r in self:
            r.sla_ids = slas.filtered(lambda sla:
                                     r.priority_level >= sla.minimum_priority and
                                     r.team_id == sla.team_id and
                                     (not sla.ticket_type_ids or r.ticket_type_id in sla.ticket_type_ids) and
                                     (not sla.tag_ids or r.tag_ids in sla.tag_ids)
                                     )

    @api.depends('sla_ids')
    def _compute_sla_line_ids(self):
        for r in self:
            sla_lines_exists = r.sla_line_ids.filtered(lambda line: line.sla_id in r.sla_ids)
            sla_lines = [(6, 0, sla_lines_exists.ids)]
            sla_lines.extend([(0, 0, {'sla_id': sla.id, 'ticket_id': r.id}) for sla in r.sla_ids.filtered(lambda sla: sla not in sla_lines_exists.sla_id)])
            r.sla_line_ids = sla_lines

    def _compute_access_url(self):
        super(HelpdeskTicket, self)._compute_access_url()
        for ticket in self:
            ticket.access_url = '/my/tickets/%s' % (ticket.id)

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for r in self:
            if r.kanban_state == 'normal':
                r.kanban_state_label = r.legend_normal
            elif r.kanban_state == 'blocked':
                r.kanban_state_label = r.legend_blocked
            else:
                r.kanban_state_label = r.legend_done

    @api.depends('team_id')
    def _compute_customer_ratings(self):
        for r in self:
            r.rating_status = r.team_id.rating_status or 'no'
            r.rating_status_period = r.team_id.rating_status_period
            r.portal_show_rating = r.team_id.portal_show_rating

    @api.constrains('stage_id')
    def _check_constrains_stage_id(self):
        stage_cancelled = self.env.ref('viin_helpdesk.helpdesk_stage_cancelled', raise_if_not_found=False)
        if stage_cancelled and not self.env.user.has_group('viin_helpdesk.group_helpdesk_user'):
            for r in self.filtered(lambda t: t.stage_id.id == stage_cancelled.id):
                # Prevent the User changing the stage to Cancel
                if r.team_id.team_leader_id.id != self.env.user.id:
                    raise ValidationError(_("You do not have the right set to Cancelled for Ticket '%s',"
                                            " only the Team Leader can do this.") % r.name)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.email_from = self.partner_id.email
        else:
            self.email_from = False

    @api.onchange('team_id')
    def _onchange_team_id(self):
        if self.team_id:
            self.stage_id = self.team_id.stage_ids and self.team_id.stage_ids[0]
            if not self.user_id:
                self.user_id = self.team_id._get_user_to_assign()

    @api.model_create_multi
    def create(self, vals_list):
        self = self.with_context(first_stage=True, force_author=True)
        for vals in vals_list:
            team_id = vals.get('team_id', False)
            if team_id:
                team = self.env['helpdesk.team'].browse(team_id)
                vals['message_partner_ids'] = (4, team.team_leader_id.id, 0)
                if not vals.get('stage_id', False):
                    vals['stage_id'] = team.stage_ids and team.stage_ids[0].id
                if not vals.get('user_id', False):
                    vals['user_id'] = team._get_user_to_assign()
        tickets = super(HelpdeskTicket, self).create(vals_list)

        tickets._add_followers()
        return tickets

    def write(self, vals):
        Team = self.env['helpdesk.team']
        for r in self:
            if vals.get('team_id', False) and not vals.get('user_id', False):
                vals['user_id'] = Team.browse(vals['team_id'])._get_user_to_assign()

        stage_id = vals.get('stage_id', False)

        # This override make sure internal users who have read access to a ticket can always change its kanban state
        # or log note with attachment
        if ('kanban_state' in vals or 'message_main_attachment_id' in vals) and len(vals) == 1 and self.env.user.has_group('base.group_user') and self.check_access_rights('read'):
            apply_sudo = False
            self.check_access_rule('read')
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except Exception:
                apply_sudo = True
            if apply_sudo:
                self = self.sudo()
        else:
            # make sure the vals has only stage_id
            if stage_id and len(vals) == 1:
                vals.update({'kanban_state': 'normal'})
                # team leader, internal user and assigned user can change ticket's stage
                user = self.env.user
                if user == self.team_id.team_leader_id \
                   or user == self.user_id \
                   or (user.has_group('base.group_user') and user == self.create_uid):
                    self = self.sudo()

        res = super(HelpdeskTicket, self).write(vals)

        # rating on stage
        if stage_id:
            self.filtered(lambda x: x.rating_status == 'stage')._send_ticket_rating_mail(force_send=True)
        self._add_followers()
        return res

    def unlink(self):
        return super(HelpdeskTicket, self).unlink()

    # View Rating of Customer
    def action_view_all_rating(self):
        """ Return the action to see all the rating of the Ticket, and activate default filters """
        self.ensure_one()
        if self.portal_show_rating:
            return {
                'type': 'ir.actions.act_url',
                'name': "Redirect to the Website Helpdesk Ticket Rating Page",
                'target': 'self',
                'url': "/ticket/rating/%s" % (self.id,)
            }
        action = self.env['ir.actions.act_window']._for_xml_id('viin_helpdesk.rating_rating_action_view_ticket')
        action['name'] = _('Ratings of %s') % (self.name,)
        action_context = safe_eval(action['context']) if action['context'] else {}
        action_context.update(self._context)
        action_context['search_default_res_name'] = self.name
        action_context.pop('group_by', None)
        return dict(action, context=action_context)

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, "%s (#%s)" % (r.name, r.id)))
        return result

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name', ''):
            default['name'] = _("%s (copy)") % self.name
        return super(HelpdeskTicket, self).copy(default)

    def _rating_get_parent_field_name(self):
        """Return helpdesk ticket parent field name for rating.parent.mixin"""
        return 'team_id'

    def prepare_partner_to_mail_template_data(self):
        self.ensure_one()
        partners = self.user_id.partner_id | self.team_id.team_leader_id.partner_id
        if self.send_notification_email:
            partners |= self.partner_id
        return ','.join(map(str, partners.ids))

    def _track_template(self, changes):
        res = super(HelpdeskTicket, self)._track_template(changes)
        mail_template_id = self.stage_id.mail_template_id
        if 'stage_id' in changes and mail_template_id:
            res['stage_id'] = (mail_template_id, {
                'auto_delete_message': True,
                'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid': 'mail.mail_notification_light'
            })
        return res

    def get_lang(self):
        # Use to select the language of email template has been sent when changing the stage of ticket
        self.ensure_one()
        return self.partner_id.lang or self.team_id.team_leader_id.partner_id.lang

    def _send_ticket_rating_mail(self, force_send=False):
        for r in self:
            rating_template = r.stage_id.rating_template_id
            lang = r.get_lang()
            if rating_template and lang:
                r.rating_send_request(rating_template, lang, force_send=force_send)

    def _cron_send_rating_ticket(self):
        tickets = self.search([('rating_status', '=', 'periodic')])
        for ticket in tickets:
            ticket._send_ticket_rating_mail()

    def _add_followers(self):
        for r in self:
            # Check if ticket is new and creator is not team leader, the invitation will be sent
            leader = r.team_id.team_leader_id
            message_partner_ids = r.sudo().message_partner_ids
            if leader.partner_id and leader.partner_id not in message_partner_ids and r._context.get('force_author',False) and r.create_uid != leader:
                model_name = self.env['ir.model']._get(r._name).display_name
                subject = _("%s: %s have been created for the %s Team") % (model_name, r.display_name, r.team_id.name)
                body = _("Hello, <a href='/mail/view?%s' data-oe-model='%s' data-oe-id='%d'>%s: %s</a> have been created for the %s Team. You can assign a user to process it.") \
                      % (url_encode({'model': r._name, 'res_id': r.id}), r._name, r.id, model_name, r.display_name, r.team_id.name)
                r.with_user(SUPERUSER_ID).message_notify(partner_ids=leader.partner_id.ids,
                                                         subject=subject,
                                                         body=body)
            partners = leader.partner_id | r.user_id.partner_id | r.partner_id
            # To avoid adding to already following partners
            r.message_subscribe((partners - message_partner_ids).ids)

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'kanban_state_label' in init_values and self.kanban_state == 'blocked':
            return self.env.ref('viin_helpdesk.mt_ticket_blocked')
        elif 'kanban_state_label' in init_values and self.kanban_state == 'done':
            return self.env.ref('viin_helpdesk.mt_ticket_ready')
        elif 'stage_id' in init_values:
            return self.env.ref('viin_helpdesk.mt_ticket_stage')
        return super(HelpdeskTicket, self)._track_subtype(init_values)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        self.ensure_one()

        partner_ids = kwargs.get('partner_ids', [])
        channel_ids = kwargs.get('channel_ids', [])

        # add partners, channels to Followers list when mentioning
        self.message_subscribe(partner_ids=partner_ids, channel_ids=channel_ids)

        # send notif to team_leader_id if ticket's kanban_state_label is changed
        trackings = kwargs.get('tracking_value_ids', [])
        if trackings:
            partner = self.team_id.team_leader_id.partner_id
            if partner and self.team_id.team_leader_id != self.env.user:
                for tracking in trackings:
                    if tracking[-1]['field'] == 'kanban_state_label':
                        kwargs['partner_ids'] = partner_ids + [partner.id]
        return super(HelpdeskTicket, self).message_post(**kwargs)

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """Add contact_name, email_from and description from email for the ticket
        """
        res = super(HelpdeskTicket, self).message_new(msg_dict, custom_values=custom_values)
        if isinstance(res, self.env['helpdesk.ticket'].__class__):
            vals = {}

            partner_id = False
            if res.create_uid.share:
                partner_id = res.create_uid.partner_id.id

            email = tools.email_split_tuples(msg_dict.get('email_from', ''))
            if email and len(email[0]) == 2:
                vals.update({
                    'contact_name': email[0][0],
                    'email_from': email[0][1],
                    })

                if not partner_id:
                    partner_id = self.env['res.partner'].search([('email_normalized', '=', email[0][1])], limit=1).id

            vals.update({
                'partner_id': partner_id,
                'description': msg_dict.get('body', ''),
                })

            res.write(vals)
        return res

    def rating_apply(self, rate, token=None, feedback=None, subtype_xmlid=None):
        return super(HelpdeskTicket, self).rating_apply(rate, token=token, feedback=feedback, subtype_xmlid='viin_helpdesk.mt_ticket_rating')

    def _message_track_post_template(self, changes):
        if self._context.get('force_author',False):
            self = self.with_user(SUPERUSER_ID)
        return super(HelpdeskTicket,self)._message_track_post_template(changes)
