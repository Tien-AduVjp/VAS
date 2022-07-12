from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Ticket2TaskWizard(models.TransientModel):
    _name = 'ticket2task.wizard'
    _description = 'Convert Ticket to Task'

    partner_id = fields.Many2one('res.partner', string='Partner', help="You can choose a partner if you want them to follow this ticket.")
    ticket_ids = fields.Many2many('helpdesk.ticket', string='Tickets', required = True)
    tag_ids = fields.Many2many('project.tags', string='Tag')
    assign_to_me = fields.Boolean(string='Assign To Me')
    project_id = fields.Many2one('project.project', string='Project', required = True,
                                 help="Project which the tasks and timesheets will be used.")
    date_deadline = fields.Date(string='Deadline', index=True, copy=False)

    @api.model
    def default_get(self, fields):
        res = super(Ticket2TaskWizard, self).default_get(fields)

        res_ids = self.env.context.get('active_ids', [])
        ticket = self.env['helpdesk.ticket'].browse(res_ids)
        if 'partner_id' in fields and not res.get('partner_id', False) and ticket.partner_id:
            res['partner_id'] = ticket.partner_id[0].id
        res['ticket_ids'] = res_ids
        return res

    def action_create_task(self):
        """ Convert ticket to task."""
        tasks = self.ticket_ids._convert_tasks(self)
        self.ticket_ids.filtered(lambda t: t.active).toggle_active()
        return self.with_context(active_test=False, create_task = tasks.ids).ticket_ids.action_tasks_view()
