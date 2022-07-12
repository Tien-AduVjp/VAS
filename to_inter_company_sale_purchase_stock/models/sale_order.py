from odoo import models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_inter_comp_purchase_order_data(self, company, company_partner):
        """ Generate purchase order values, from the SO (self)
        """
        res = super(SaleOrder, self)._prepare_inter_comp_purchase_order_data(company, company_partner)

        # find location and warehouse, pick warehouse from company object
        PurchaseOrder = self.env['purchase.order']
        warehouse = company.inter_comp_warehouse_id and company.inter_comp_warehouse_id.company_id.id == company.id and company.inter_comp_warehouse_id or False
        if not warehouse:
            raise UserError(_('Configure correct warehouse for company (%s) from Menu: Settings/Users/Companies') % company.name)

        picking_type_id = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'), ('warehouse_id', '=', warehouse.id)
        ], limit=1)
        if not picking_type_id:
            inter_comp_user = self.partner_id._get_inter_comp_user()
            picking_type_id = PurchaseOrder.with_user(inter_comp_user.id)._default_picking_type()
        res.update({
            'picking_type_id': picking_type_id.id,
        })
        return res
