from odoo import models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    """
        Disallow to delete a sale order that is related by any stock transfer
    """
    def unlink(self):
        for r in self:
            if r.company_id.prevent_unlink_related_pickings and r.picking_ids:
                display_message = _("You cannot delete the sale order '%s' "
                    "while it is still referred by the stock transfer '%s'!\n"
                    "\n"
                    "You may cancel the order instead."
                ) % (r.name, r.picking_ids[0].name)    
                raise UserError(display_message)
        return super(SaleOrder, self).unlink()
