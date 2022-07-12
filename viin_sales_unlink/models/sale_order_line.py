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
            if r.company_id.prevent_unlink_sales_having_invoices and r.invoice_lines:
                raise UserError(_("You may not be able to remove the order line `%s` of the order `%s` while it is still referred by the invoice line `%s` of the invoice `%s`.\n"
                    "Please remove all the referenced invoice lines first.")
                    % (r.name, r.order_id.name, r.invoice_lines[0].name, r.invoice_lines[0].move_id.display_name)
                    )
        return super(SaleOrderLine, self).unlink()
