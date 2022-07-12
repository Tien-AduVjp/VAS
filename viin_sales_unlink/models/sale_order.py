from odoo import models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def unlink(self):
        """
          The case here is to delete an order that has been confirmed and now not in "sale" state:
            -) only allows to delete this order if it has no invoice related.
        """
        for r in self:
            if r.company_id.prevent_unlink_sales_having_invoices and r.invoice_ids:
                raise UserError(_("You may not be able to delete the sale order '%s' while it is still referred by the invoice `%s`.\n"
                    "Please remove all the reference invoices first.")
                    % (r.name, r.invoice_ids[0].display_name))
        return super(SaleOrder, self).unlink()
