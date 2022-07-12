from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Lead2TicketWizard(models.TransientModel):
    _name = 'lead2ticket.wizard'
    _description = 'Convert Lead/Opportunity to Ticket'

    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string='Ticket Type', help="Used to classify question type for customer")
    tag_ids = fields.Many2many('helpdesk.tag', string="Tags")
    team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team', required=True, help="Used to classify support group for customer")
    lead_ids = fields.Many2many('crm.lead', string='Leads')
    partner_id = fields.Many2one('res.partner', string='Partner', help="You can choose a partner if you want them to follow this ticket.")
    send_notification_email = fields.Boolean(string='Send Notification Email',
                                             help="If set, then an email will be sent to the partner when the ticket changes stage.")
    assign_to_me = fields.Boolean(string='Assign To Me')
    is_team_member = fields.Boolean(string='Is Team Member', compute='_compute_is_tem_member', store=True)

    @api.model
    def default_get(self, fields):
        """ Default find all existing lead/opportunity links to merge all information together"""
        res = super(Lead2TicketWizard, self).default_get(fields)

        res_ids = self.env.context.get('active_ids', [])

        leads = self.env['crm.lead'].browse(res_ids)
        if not leads:
            raise UserError(_("Please select more than one element (lead or opportunity)."))

        if 'partner_id' in fields and not res.get('partner_id', False) and leads.partner_id:
            res['partner_id'] = leads.partner_id[0].id
        if 'ticket_type_id' in fields and not res.get('ticket_type_id', False):
            res['ticket_type_id'] = self.env.ref('viin_helpdesk.helpdesk_ticket_type_question').id
        if 'team_id' in fields and not res.get('team_id', False):
            res['team_id'] = self.env.company.default_helpdesk_team_id.id
        res['lead_ids'] = res_ids
        return res

    @api.depends('team_id.team_member_ids')
    def _compute_is_tem_member(self):
        for r in self:
            if r.env.user in r.team_id.team_member_ids:
                r.is_team_member = True
            else:
                r.is_team_member = False

    def action_create_ticket(self):
        """ Convert lead to opportunity or merge lead and opportunity and open
            the freshly created opportunity view.
        """
        #If converting to ticket, lead's company must be the same as the helpdesk team
        for lead in self.lead_ids.filtered(lambda l: l.company_id):
            if lead.company_id != self.team_id.company_id:
                raise UserError(_("Company of lead '%s' must be the same as the helpdesk team!") % lead.name)
        self.lead_ids._convert_tickets(self)
        self.lead_ids.write({'active': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.model
    def view_init(self, fields):
        """ Check some preconditions before the wizard executes. """
        for lead in self.lead_ids:
            if lead.probability == 100:
                raise UserError(_("Closed/Dead leads/opportunities cannot be converted into ticket."))
        return False
