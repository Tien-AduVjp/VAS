from odoo import _, fields, models
from odoo.tools import html2plaintext


class Task(models.Model):
    _inherit = 'project.task'

    ticket_ids = fields.One2many('helpdesk.ticket', 'task_id', string='Helpdesk Tickets')
    tickets_count = fields.Integer(string='Tickets', compute='_compute_tickets_count')
    
    def _compute_tickets_count(self):
        tickets_data = self.env['helpdesk.ticket'].read_group([('task_id', 'in', self.ids)], ['task_id'], ['task_id'])
        mapped_data = dict([(dict_data['task_id'][0], dict_data['task_id_count']) for dict_data in tickets_data])
        for r in self:
            r.tickets_count = mapped_data.get(r.id, 0)
    
    def action_tickets_view(self):
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_name': self[:1].name,
            'default_description': html2plaintext(self[:1].description),
            'default_company_id': self.env.company.id,
            'default_team_id': self.env.company.default_helpdesk_team_id.id,
            'default_task_id': self[:1].id,
            'default_partner_id': self[:1].partner_id.id or self[:1].project_id.partner_id.id,
            })
        
        view_mode = 'kanban,tree,form,pivot,calendar,graph'
        action = {
            'name': _('Tickets'),
            'view_mode': view_mode,
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('id', 'in', self.ticket_ids.ids)],
        }
        if len(self.ticket_ids) == 1 and not ctx.get('create_new_ticket', False):
            action.update({
                'view_mode': 'form',
                'res_id': self.ticket_ids.id
            })
        return action

    def _prepare_ticket_vals(self, wizard):
        self.ensure_one()
        vals = {
            'name': self.name,
            'ticket_type_id': wizard.ticket_type_id.id,
            'tag_ids': wizard.tag_ids.ids,
            'team_id': wizard.team_id.id,
            'user_id': wizard.assign_to_me and self.env.user.id,
            'partner_id': wizard.partner_id.id,
            'company_id': wizard.team_id.company_id.id,
            'task_id': self.id,
            'project_id': wizard.team_id.project_id and wizard.team_id.project_id.id or self.project_id.id,
            'send_notification_email': wizard.send_notification_email,
            }
        if self.description:
            vals['description'] = html2plaintext(self.description)
        return vals
    
    def _prepare_ticket_vals_list(self, wizard):
        vals_list = []
        for r in self:
            vals_list.append(r._prepare_ticket_vals(wizard))
        return vals_list
    
    def _convert_tickets(self, wizard):
        vals_list = self._prepare_ticket_vals_list(wizard)
        tickets = self.env['helpdesk.ticket'].create(vals_list)
        # move attachments and messages to tickets
        all_attachments = self.env['ir.attachment'].search([('res_model', '=', 'project.task'), ('res_id', 'in', self.ids)])
        for ticket in tickets:
            attachments = all_attachments.filtered(lambda att: att.res_id == ticket.task_id.id)
            if attachments:
                attachments.write({'res_model': 'helpdesk.ticket', 'res_id': ticket.id})
            messages = ticket.task_id.message_ids
            if messages:
                messages.write({'model': 'helpdesk.ticket', 'res_id': ticket.id})
            if ticket.team_id.project_id:
                if ticket.task_id and ticket.task_id.project_id != ticket.team_id.project_id:
                    ticket.task_id.write({
                        'project_id': ticket.team_id.project_id.id
                        })
        return tickets
