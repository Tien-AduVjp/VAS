from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Task2TicketWizard(models.TransientModel):
    _name = 'task2ticket.wizard'
    _description = 'Convert Task to Ticket'

    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string='Ticket Type', help="Used to classify question type for customer")
    tag_ids = fields.Many2many('helpdesk.tag', string="Tags")
    team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team', required=True, help="Used to classify support group for customer")
    task_ids = fields.Many2many('project.task', string='Tasks')
    partner_id = fields.Many2one('res.partner', string='Partner', help="You can choose a partner if you want them to follow this ticket.")
    send_notification_email = fields.Boolean(string='Send Notification Email',
                                             help="If set, then an email will be sent to the partner when the ticket changes stage.")
    assign_to_me = fields.Boolean(string='Assign To Me')
    is_team_member = fields.Boolean(string='Is Team Member', compute='_compute_is_tem_member', store=True)

    @api.model
    def default_get(self, fields):
        res = super(Task2TicketWizard, self).default_get(fields)

        res_ids = self.env.context.get('active_ids', [])

        tasks = self.env['project.task'].browse(res_ids)
        if not tasks:
            raise UserError(_("Please select more than one task."))

        if 'partner_id' in fields and not res.get('partner_id', False) and tasks.partner_id:
            res['partner_id'] = tasks.partner_id[0].id
        if 'ticket_type_id' in fields and not res.get('ticket_type_id', False):
            res['ticket_type_id'] = self.env.ref('viin_helpdesk.helpdesk_ticket_type_question').id
        if 'team_id' in fields and not res.get('team_id', False):
            team_id = tasks[:1].project_id.helpdesk_team_id or self.env['helpdesk.team'].search([('company_id', '=', self.env.company.id)], limit=1)
            res['team_id'] = team_id.id
        res['task_ids'] = res_ids
        return res

    @api.depends('team_id.team_member_ids')
    def _compute_is_tem_member(self):
        for r in self:
            if r.env.user in r.team_id.team_member_ids:
                r.is_team_member = True
            else:
                r.is_team_member = False

    def action_create_ticket(self):
        """ Convert task to ticket."""
        # If converting to ticket, task's company must be the same as the helpdesk team
        for task in self.task_ids.filtered(lambda t: t.company_id):
            if task.company_id != self.team_id.company_id:
                raise UserError(_("Company of task '%s' must be the same as the helpdesk team!") % task.name)
        self.task_ids._convert_tickets(self)
        self.task_ids.filtered(lambda t: t.active).toggle_active()
        return self.with_context(active_test=False).task_ids.action_tickets_view()
