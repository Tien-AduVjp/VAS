from odoo import models, _
from odoo.tools import html2plaintext, html_escape


class MailChannel(models.Model):
    _inherit = 'mail.channel'
    
    def _define_command_ticket(self):
        return {'help': _("Create a new helpdesk ticket (/ticket ticket title)")}
    
    def _execute_command_ticket(self, **kwargs):
        self.ensure_one()
        command = kwargs.get('body', '').split()
        partner = self.env.user.partner_id
        message = ''
        if command[0].strip().lower() == '/ticket':
            if len(command) == 1:
                message = _("Please enter ticket title after '/ticket' command to create a new helpdesk ticket")
            else:
                ticket_subject = command[1:]
                ticket_description = ''.join(
                    '%s: %s\n' % (message.author_id.name or self.anonymous_name, message.body)
                    for message in self.channel_message_ids.sorted('id')
                )
                
                channel_partner = self.env['mail.channel.partner'].search([
                    ('partner_id', '!=', partner.id),
                    ('channel_id', '=', self.id)], limit=1)
                
                helpdesk_ticket = self.env['helpdesk.ticket'].create({
                    'name': ' '.join(ticket_subject),
                    'description': html2plaintext(ticket_description),
                    'partner_id': channel_partner.partner_id.id,
                })
                helpdesk_ticket._onchange_partner_id()
                message = _('New helpdesk ticket has created: <a href="#" data-oe-id="%s" data-oe-model="helpdesk.ticket">%s</a>') \
                    % (helpdesk_ticket.id, html_escape(helpdesk_ticket.name))
        return self._send_transient_message(partner, message)
