from odoo import fields, models, _
from odoo import tools
from odoo.tools import plaintext2html


class Lead(models.Model):
    _inherit = "crm.lead"

    ticket_count = fields.Integer(string='Tickets Count', compute='_compute_ticket_count')
    ticket_ids = fields.One2many('helpdesk.ticket', 'lead_id', string='Tickets')

    def _compute_ticket_count(self):
        leads_data = self.env['helpdesk.ticket'].read_group([('lead_id', 'in', self.ids)], ['lead_id'], ['lead_id'])
        mapped_data = dict([(dict_data['lead_id'][0], dict_data['lead_id_count']) for dict_data in leads_data])
        for r in self:
            r.ticket_count = mapped_data.get(r.id, 0)

    def action_tickets_view(self):
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_name': self[:1].name,
            'default_description': plaintext2html(self[:1].description),
            'default_company_id': self.env.company.id,
            'default_team_id': self.env.company.default_helpdesk_team_id.id,
            'default_lead_id': self[:1].id,
            'default_partner_id': self[:1].partner_id.id,
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
            'lead_id': self.id,
            'send_notification_email': wizard.send_notification_email,
            }
        if self.email_from:
            email = tools.email_split_tuples(self.email_from)
            if email and len(email[0]) == 2:
                vals.update({
                    'contact_name': email[0][0],
                    'email_from': email[0][1],
                    })
            else:
                vals.update({
                    'email_from': self.email_from,
                    })
        if self.description:
            vals['description'] = plaintext2html(self.description)
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
        all_attachments = self.env['ir.attachment'].search([('res_model', '=', 'crm.lead'), ('res_id', 'in', self.ids)])
        for ticket in tickets:
            attachments = all_attachments.filtered(lambda att: att.res_id == ticket.lead_id.id)
            if attachments:
                attachments.write({'res_model': 'helpdesk.ticket', 'res_id': ticket.id})
            messages = ticket.lead_id.message_ids
            if messages:
                messages.write({'model': 'helpdesk.ticket', 'res_id': ticket.id})

        return tickets

    def merge_opportunity(self, user_id=False, team_id=False, auto_unlink=True):
        tickets = self.ticket_ids
        res = super(Lead, self).merge_opportunity(user_id, team_id, auto_unlink)
        res.ticket_ids = tickets
        return res
