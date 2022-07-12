from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import html2plaintext, html_escape


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    def _define_command_social_lead(self):
        return {'help': _('Create a new lead (/social_lead lead title)')}

    def _execute_command_social_lead(self, **kwargs):
        if self.channel_type != 'social_chat':
            raise UserError(_("You cannot generate leads from non-social chat channels with this command"))

        partner = self.env.user.partner_id
        key = kwargs['body']
        channel_partners = self.env['mail.channel.partner'].search([
            ('partner_id', '!=', partner.id),
            ('channel_id', '=', self.id)], limit=1
        )
        if key.strip() == '/social_lead':
            msg = self._define_command_social_lead()['help']
        else:
            lead = self._convert_social_visitor_to_lead(partner, channel_partners, key)
            msg = _('Created a new lead: <a href="#" data-oe-id="%s" data-oe-model="crm.lead">%s</a>') % (
                lead.id, html_escape(lead.name))
        self._send_transient_message(partner, msg)

    def _convert_social_visitor_to_lead(self, partner, channel_partners, key):
        description = ''.join(
            '%s: %s\n' % (message.author_id.name or self.social_user_name, message.body)
            for message in self.channel_message_ids.sorted('id')
        )
        customers = self.env['res.partner']
        for customer in channel_partners.partner_id.filtered('partner_share').with_context(active_test=False):
            if customer.user_ids and all(user._is_public() for user in customer.user_ids):
                customers = self.env['res.partner']
                break
            else:
                customers |= customer

        source_id = self.social_page_id.source_id
        if not source_id:
            source_id = self.env['utm.source'].create({
                'name': '%s %s' % (self.social_page_id.social_provider.capitalize(), self.social_page_id.name)
            })
            self.social_page_id.source_id = source_id

        return self.env['crm.lead'].create({
            'name': html2plaintext(key[13:]),
            'partner_id': customers[0].id if customers else False,
            'user_id': False,
            'team_id': False,
            'description': html2plaintext(description),
            'referred': partner.name,
            'source_id': source_id.id
        })
