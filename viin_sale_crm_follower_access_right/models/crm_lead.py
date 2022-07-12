from odoo import models, api
from odoo.exceptions import AccessError


class Lead(models.Model):
    _inherit = 'crm.lead'
    _mail_post_access = 'read'

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        if self.check_access_rights('read', raise_exception=False):
            self.check_access_rule('read')
            try:
                self.check_access_rule('write')
            except AccessError:
                return super(Lead, self.sudo()).message_subscribe(partner_ids, channel_ids, subtype_ids)
        return super(Lead, self).message_subscribe(partner_ids, channel_ids, subtype_ids)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        return super(Lead, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
