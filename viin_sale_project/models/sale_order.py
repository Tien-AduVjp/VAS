from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def read(self, fields=None, load='_classic_read'):
        """
        Although project users could have read access but error would still be raised if
        they didn't have access right to the documents that link to the sales order (e.g. stock.picking).
        his override ensures no such error will be raised if they have read access to the sales order
        """
        if self.check_access_rights('read', raise_exception=False) and self.env.user.has_group('project.group_project_user'):
            self.check_access_rule('read')
            return super(SaleOrder, self.sudo()).read(fields, load)
        return super(SaleOrder, self).read(fields, load)
