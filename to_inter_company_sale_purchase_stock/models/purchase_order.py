from odoo import models, _
from odoo.exceptions import Warning


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_inter_comp_sale_order_data(self):
        """ Generate the Sales Order values from the PO
        """
        vals = super(PurchaseOrder, self)._prepare_inter_comp_sale_order_data()
        company = self.partner_id._find_company()
        warehouse = company.inter_comp_warehouse_id and company.inter_comp_warehouse_id.company_id.id == company.id and company.inter_comp_warehouse_id or False
        if not warehouse:
            raise Warning(_('Configure correct warehouse for company (%s) from Menu: Settings/Users/Companies') % company.name)
        vals.update({
            'warehouse_id': warehouse.id
        })
        return vals
