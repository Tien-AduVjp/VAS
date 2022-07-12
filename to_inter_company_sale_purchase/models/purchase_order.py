from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    auto_generated = fields.Boolean(string='Auto Generated Purchase Order', copy=False)
    inter_comp_sale_order_id = fields.Many2one('sale.order', string='Inter-Company Sale Order', readonly=True, copy=False)

    def button_cancel(self):
        for r in self.filtered(lambda po: po.inter_comp_sale_order_id):
            inter_comp_user = r.partner_id._get_inter_comp_user()
            r.with_user(inter_comp_user.id).inter_comp_sale_order_id.message_post(
                body=_("The inter-company invoice %s of the company %s was cancelled. Please contact that company to solve the issue.") % (r.name, r.company_id.name)
                )
        super(PurchaseOrder, self).button_cancel()

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_rfq_as_sent'):
            for order in self:
                order.create_if_not_exist_inter_company_sale_order()
        return super(PurchaseOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def button_approve(self, force=False):
        """ Generate inter company sales order base on conditions."""
        res = super(PurchaseOrder, self).button_approve(force=force)
        for order in self:
            company_rec = order.create_if_not_exist_inter_company_sale_order()
            if company_rec and company_rec.so_po_auto_validation == 'validated' and company_rec.intercompany_user_id and order.inter_comp_sale_order_id:
                order.inter_comp_sale_order_id.with_context(force_company=company_rec.id).with_user(company_rec.intercompany_user_id.id).action_confirm()
        return res

    def create_if_not_exist_inter_company_sale_order(self):
        # get the company from partner then trigger action of intercompany relation
        company_rec = self.partner_id._find_company()
        if company_rec and company_rec != self.company_id and company_rec.applicable_on in ('purchase', 'sale_purchase') and (not self.auto_generated) and (not self.inter_comp_sale_order_id):
            self._generate_inter_comp_sale_order()
        return company_rec

    def _generate_inter_comp_sale_order(self):
        """ Create a Sales Order from the current PO (self)
            Note : In this method, reading the current PO is done as sudo, and the creation of the derived
            SO as intercompany_user, minimizing the access right required for the trigger user.
        """
        company = self.partner_id._find_company()
        self = self.with_context(force_company=company.id)
        SaleOrder = self.env['sale.order']

        # find user for creating and validation SO/PO from partner company
        inter_comp_user = self.partner_id._get_inter_comp_user()
        # check intercompany user access rights
        if not SaleOrder.with_user(inter_comp_user.id).check_access_rights('create', raise_exception=False):
            raise Warning(_("Inter company user of company %s doesn't have enough access rights") % company.name)

        # check pricelist currency should be same with SO/PO document
        company_partner = self.company_id.partner_id.with_user(inter_comp_user.id)
        if self.currency_id.id != company_partner.property_product_pricelist.currency_id.id:
            raise Warning(_("Could not generate sales order for the company of the vendor while the currency of vendor's sales pricelist differs from the purchase order's currency."
                            " You should change the currency of the purchase order to %s.")
                            % company_partner.property_product_pricelist.currency_id.name)

        # create the SO and generate its lines from the PO lines
        SaleOrderLine = self.env['sale.order.line']
        # read it as sudo, because inter-compagny user can not have the access right on PO
        sale_order_data = self.sudo()._prepare_inter_comp_sale_order_data()
        sale_order = SaleOrder.with_user(inter_comp_user.id).create(sale_order_data)
        # lines are browse as sudo to access all data required to be copied on SO line (mainly for company dependent field like taxes)
        for line in self.order_line.sudo():
            so_line_vals = line._prepare_inter_comp_sale_order_line_data(sale_order)
            inter_comp_sale_line_id = SaleOrderLine.with_user(inter_comp_user.id).create(so_line_vals)
            if inter_comp_sale_line_id:
                line.write({'inter_comp_sale_order_line_id': inter_comp_sale_line_id.id})

        update_vals = {'inter_comp_sale_order_id': sale_order.id}
        # write vendor reference field on PO
        if not self.partner_ref:
            update_vals.update({'partner_ref': sale_order.name})
        self.write(update_vals)

    def _prepare_inter_comp_sale_order_data(self):
        """ Generate the Sales Order values from the PO
        """
        company = self.partner_id._find_company()
        inter_comp_user = self.partner_id._get_inter_comp_user()
        partner = self.company_id.partner_id.with_user(inter_comp_user.id)
        partner_addr = partner.sudo().address_get(['invoice', 'delivery', 'contact'])
        direct_delivery_address = self.dest_address_id and self.dest_address_id.id or partner_addr['delivery'] or False
        return {
            'name': self.env['ir.sequence'].sudo().next_by_code('sale.order') or '/',
            'company_id': company.id,
            'client_order_ref': self.name,
            'partner_id': partner.id,
            'pricelist_id': partner.property_product_pricelist.id,
            'partner_invoice_id': partner_addr['invoice'],
            'date_order': self.date_order,
            'fiscal_position_id': partner.property_account_position_id.id,
            'payment_term_id': partner.property_payment_term_id.id,
            'user_id': False,
            'auto_generated': True,
            'inter_comp_purchase_order_id': self.id,
            'partner_shipping_id': direct_delivery_address
        }

    def action_view_invoice(self):
        create_bill = self.env.context.get('create_bill', False)
        auto_generated_order = self.filtered(lambda x: x.auto_generated)
        if auto_generated_order and (len(self.mapped('invoice_ids')) == 0 or create_bill):
            raise ValidationError(_("These purchase order(s): '%s' were auto generated by inter company transactions, so you can't create bills for them."
                                    "These bills will be auto generated when the supplier invoices were validated.") % ' ,'.join(auto_generated_order.mapped('name')))
        return super(PurchaseOrder, self).action_view_invoice()
