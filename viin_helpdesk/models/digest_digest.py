from odoo import fields, models, _
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_helpdesk_ticket_opened = fields.Boolean('Open Tickets')
    kpi_helpdesk_ticket_opened_value = fields.Integer(compute='_compute_helpdesk_ticket_opened_value')
    kpi_helpdesk_ticket_closed = fields.Boolean('Close Tickets')
    kpi_helpdesk_ticket_closed_value = fields.Integer(compute='_compute_helpdesk_ticket_closed_value')

    def _check_access_right(self):
        if not self.env.user.has_group('viin_helpdesk.group_helpdesk_user'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))

    def _compute_helpdesk_ticket_opened_value(self):
        self._check_access_right()
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            ticket_opened = self.env['helpdesk.ticket'].search_count([
                ('create_date', '>=', start),
                ('create_date', '<', end),
                ('company_id', '=', company.id),
                '&', ('stage_id.fold', '=', False), ('stage_id.is_final_stage', '=', False),
            ])
            record.kpi_helpdesk_ticket_opened_value = ticket_opened

    def _compute_helpdesk_ticket_closed_value(self):
        self._check_access_right()
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            ticket_closed = self.env['helpdesk.ticket'].search_count([
                ('create_date', '>=', start),
                ('create_date', '<', end),
                ('company_id', '=', company.id),
                '|', ('stage_id.fold', '=', True), ('stage_id.is_final_stage', '=', True),
            ])
            record.kpi_helpdesk_ticket_closed_value = ticket_closed

    def compute_kpis_actions(self, company, user):
        res = super(Digest, self).compute_kpis_actions(company, user)
        res['kpi_helpdesk_ticket_opened'] = 'viin_helpdesk.all_tickets_action&menu_id=%s' % self.env.ref('viin_helpdesk.all_tickets_menu').id
        return res
