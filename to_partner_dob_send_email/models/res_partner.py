from odoo import models, fields, api, tools


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_send_hbd_email = fields.Boolean(string='Send Happy Birthday Email', company_dependent=True)
    property_hbd_email_template_id = fields.Many2one('mail.template', company_dependent=True, string='Happy Birthday Email Template')
    property_last_hbd_email_sent = fields.Date(string='Last Happy Birthday Email Sent', company_dependent=True,
                                               help="The technical field to store the date on which the last Happy Birthday Email"
                                               " was sent to this partner")

    @api.onchange('dob')
    def _onchange_dob(self):
        if self.dob:
            self.property_send_hbd_email = self.env.company.send_hbd_email

    @api.onchange('property_send_hbd_email')
    def _onchange_send_hbd_email(self):
        if self.property_send_hbd_email and not self.property_hbd_email_template_id:
            self.property_hbd_email_template_id = self.env.company.hdb_email_template_id
            
    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        default = dict(
            default or {},
            property_send_hbd_email = self.property_send_hbd_email,
            property_hbd_email_template_id = self.property_hbd_email_template_id.id
        )
        return super(ResPartner, self).copy(default=default)

    def _send_happy_birthday_email(self):
        for r in self:
            with r.env.cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                r.message_post_with_template(r.property_hbd_email_template_id.id)
                r.write({
                    'property_last_hbd_email_sent': fields.Date.today(),
                    })

    def _find_partners_having_birthday_today(self, company_ids):
        _, current_month, current_day = self.env['to.base'].split_date(fields.Date.today())

        return self.search([
            ('email', '!=', False),
            ('mob', '=', current_month),
            ('dyob', '=', current_day),
            '|', ('company_id', '=', False), ('company_id', 'in', company_ids)
        ])

    def cron_send_happy_birthday_email(self):
        companies = self.env['res.company'].search([('send_hbd_email', '=', True)])
        partners = self._find_partners_having_birthday_today(companies.ids)
        
        for company in companies:
            partners_to_send = partners.filtered(lambda p:
                                                p.property_send_hbd_email \
                                                and p.property_hbd_email_template_id \
                                                and (
                                                    not p.company_id 
                                                    or p.company_id == company) \
                                                and (
                                                    not p.property_last_hbd_email_sent 
                                                    or p.property_last_hbd_email_sent != fields.Date.today())
                                                )
            partners_to_send.with_context(company_id=company.id)._send_happy_birthday_email()
