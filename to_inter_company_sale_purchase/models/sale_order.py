from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    auto_generated = fields.Boolean(string='Auto Generated Sales Order', copy=False)
    inter_comp_purchase_order_id = fields.Many2one('purchase.order', string='Inter-Company Purchase Order', readonly=True, copy=False)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            for order in self:
                order.create_if_not_exist_inter_company_purchase_order()
        return super(SaleOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def _action_confirm(self):
        """ Generate inter company purchase order based on conditions """
        res = super(SaleOrder, self)._action_confirm()
        for order in self:
            company = order.create_if_not_exist_inter_company_purchase_order()
            # auto-validate the purchase order if needed
            if (
                company
                and company.so_po_auto_validation == 'validated'
                and company.intercompany_user_id
                and order.inter_comp_purchase_order_id
                and not order.auto_generated
            ):
                order.inter_comp_purchase_order_id.with_company(company).with_user(company.intercompany_user_id.id).button_confirm()
        return res

    def create_if_not_exist_inter_company_purchase_order(self):
        if not self.company_id:  # if company_id not found, return to normal behavior
            return False
        company = self.partner_id._find_company()
        if company and company != self.company_id and company.applicable_on in ('sale', 'sale_purchase') and (not self.auto_generated) and (not self.inter_comp_purchase_order_id):
            self.inter_company_create_purchase_order(company)
        return company

    def inter_company_create_purchase_order(self, company):
        """ Create a Purchase Order from the current SO (self)
            Note : In this method, reading the current SO is done as sudo, and the creation of the derived
            PO as intercompany_user, minimizing the access right required for the trigger user
        """
        self = self.with_context(company_id=company.id)
        PurchaseOrder = self.env['purchase.order']
        company_partner = self.with_company(company).company_id and self.with_company(company).company_id.partner_id or False
        if not company or not company_partner:
            return

        # find user for creating and validating SO/PO from company
        inter_comp_user = self.partner_id._get_inter_comp_user()
        # check intercompany user access rights
        if not PurchaseOrder.with_user(inter_comp_user.id).check_access_rights('create', raise_exception=False):
            raise UserError(_("Inter company user of company %s doesn't have enough access rights") % company.name)

        # create the PO and generate its lines from the SO
        context = self._context.copy()
        if not context.get('allowed_company_ids', False):
            context['allowed_company_ids'] = [company.id]
        elif company.id not in context['allowed_company_ids']:
            context['allowed_company_ids'].append(company.id)
        PurchaseOrderLine = self.env['purchase.order.line'].with_context(context)
        # read it as sudo, because inter-compagny user can not have the access right on PO
        po_vals = self.sudo()._prepare_inter_comp_purchase_order_data(company, company_partner)
        purchase_order = PurchaseOrder.with_user(inter_comp_user.id).create(po_vals)
        for line in self.order_line.sudo():
            po_line_vals = line._prepare_inter_comp_purchase_order_line_data(self.date_order, purchase_order, company)
            inter_comp_purchase_line = PurchaseOrderLine.with_user(inter_comp_user.id).create(po_line_vals)
            if inter_comp_purchase_line:
                line.write({'inter_comp_purchase_order_line_id': inter_comp_purchase_line.id})

        update_vals = {'inter_comp_purchase_order_id': purchase_order.id}
        # write customer reference field on SO
        if not self.client_order_ref:
            update_vals.update({'client_order_ref': purchase_order.name})
        self.write(update_vals)

    def _prepare_inter_comp_purchase_order_data(self, company, company_partner):
        """ Generate purchase order values, from the SO (self)
        """
        return {
            'name': self.env['ir.sequence'].sudo().next_by_code('purchase.order'),
            'origin': self.name,
            'partner_id': company_partner.id,
            'date_order': self.date_order,
            'company_id': company.id,
            'fiscal_position_id': company_partner.sudo().property_account_position_id.id,
            'payment_term_id': company_partner.sudo().property_supplier_payment_term_id.id,
            'auto_generated': True,
            'inter_comp_sale_order_id': self.id,
            'partner_ref': self.name,
            'currency_id': self.currency_id.id
        }

    def action_invoice_create(self, grouped=False, final=False):
        auto_generated_order = self.filtered(lambda x: x.auto_generated)
        if auto_generated_order:
            raise ValidationError(_("These sale order(s): '%s' were auto generated by inter company transactions, so you can't create invoices for them."
                                    "These invoices will be auto generated when the source invoices were validated.") % ' ,'.join(auto_generated_order.mapped('name')))
        return super(SaleOrder, self).action_invoice_create(grouped, final)
