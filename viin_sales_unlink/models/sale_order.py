from odoo import models,_
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def unlink(self):
        """
          The case here is to delete an order that has been confirmed and now not in "sale" state:
            -) only allows to delete this order if it has no invoice related.
        """
        for r in self:
            if r.company_id.prevent_unlink_related_invoices and r.invoice_ids:
                raise UserError(_("The sale order '%s' cannot be deleted because of related invoice.\n" 
                    "Please remove all the related invoices first to proceed the deletion. "
                    "(Note: you can only delete an invoice that has never been posted).") % r.name)
        return super(SaleOrder, self).unlink()
