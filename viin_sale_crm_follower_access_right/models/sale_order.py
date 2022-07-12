from odoo import models
from odoo.exceptions import AccessError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _mail_post_access = 'read'

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        if self.check_access_rights('read', raise_exception=False):
            self.check_access_rule('read')
            try:
                self.check_access_rule('write')
            except AccessError:
                return super(SaleOrder, self.sudo()).message_subscribe(partner_ids, channel_ids, subtype_ids)
        return super(SaleOrder, self).message_subscribe(partner_ids, channel_ids, subtype_ids)
