from odoo import models, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def unlink(self):
        """
            The case here is to delete order lines on a certain order
            -) only allows to delete order lines if there has no invoice lines related.
        """
        for r in self:
            if r.company_id.prevent_unlink_related_invoices and r.invoice_lines:
                raise UserError(_("The order line '%s' cannot be deleted because of related invoice lines.\n" 
                    "Please go into the corresponding invoice and " 
                    "remove all the related invoice lines first to proceed the deletion.") % r.name)
        return super(SaleOrderLine, self).unlink()
