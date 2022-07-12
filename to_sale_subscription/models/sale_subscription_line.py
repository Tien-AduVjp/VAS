from odoo import api, fields, models


class SaleSubscriptionLine(models.Model):
    _name = 'sale.subscription.line'
    _description = 'Subscription Line'

    product_id = fields.Many2one('product.product', string='Product', domain="[('recurring_invoice','=',True)]", required=True)
    subscription_id = fields.Many2one('sale.subscription', string='Subscription')
    name = fields.Text(string='Description', required=True)
    quantity = fields.Float(string='Quantity', help="Quantity that will be invoiced.", default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    discount = fields.Float(string='Discount (%)', digits='Discount')
    price_subtotal = fields.Float(compute='_compute_price_subtotal', string='Sub Total', digits='Account', store=True)

    @api.depends('price_unit', 'quantity', 'discount', 'subscription_id.pricelist_id')
    def _compute_price_subtotal(self):
        Tax = self.env['account.tax']
        for r in self:
            r_sudo = r.sudo()
            price = Tax._fix_tax_included_price(r.price_unit, r_sudo.product_id.taxes_id, Tax)
            r.price_subtotal = r.quantity * price * (100.0 - r.discount) / 100.0
            if r.subscription_id.pricelist_id:
                r.price_subtotal = r_sudo.subscription_id.pricelist_id.currency_id.round(r.price_subtotal)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        product = self.product_id
        partner = self.subscription_id.partner_id
        if partner.lang:
            product = product.with_context(lang=partner.lang)

        self.name = product.get_product_multiline_description_sale()

    @api.onchange('product_id', 'quantity')
    def _onchange_product_quantity(self):
        domain = {}
        subscription = self.subscription_id
        context = dict(self.env.context or {})
        context.update({
            'company_id': subscription.company_id.id,
            'force_company': subscription.company_id.id,
            'pricelist': subscription.pricelist_id.id,
            'quantity': self.quantity,
            })
        
        if not self.product_id:
            self.price_unit = 0.0
            domain['uom_id'] = []
        else:
            partner = subscription.partner_id.with_context(context)
            if partner.lang:
                context.update({'lang': partner.lang})

            product = self.product_id.with_context(context)
            self.price_unit = product.price

            if not self.uom_id:
                self.uom_id = product.uom_id.id
            if self.uom_id.id != product.uom_id.id:
                self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

        return {'domain': domain}

    @api.onchange('uom_id')
    def _onchange_uom_id(self):
        if not self.uom_id:
            self.price_unit = 0.0
            return {'domain': {'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}
        else:
            return self._onchange_product_quantity()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product_id = vals.get('product_id', False)
            if product_id:
                if not vals.get('name'):
                    line = self.new(vals)
                    line.onchange_product_id()
                    vals['name'] = line._fields['name'].convert_to_write(line['name'], line)
                if not vals.get('uom_id'):
                    vals['uom_id'] = self.env['product.product'].browse(product_id).uom_id.id
        return super(SaleSubscriptionLine, self).create(vals_list)

    def get_template_option_line(self):
        """ Return the account.analytic.invoice.line.option which has the same product_id as
        the invoice line"""
        if not self.subscription_id and not self.subscription_id.template_id:
            return False
        template = self.subscription_id.template_id
        return template.sudo().subscription_template_option_ids.filtered(lambda r: r.product_id == self.product_id)

    def _amount_line_tax(self):
        self.ensure_one()
        Position = self.env['account.fiscal.position']
        val = 0.0
        product = self.product_id
        product_tmp = product.sudo().product_tmpl_id
        company_id = self.subscription_id.company_id.id
        for tax in product_tmp.taxes_id.filtered(lambda t: t.company_id.id == company_id):
            partner = self.subscription_id.partner_id
            fiscal_position_id = Position.with_context(force_company=company_id).get_fiscal_position(partner.id)
            if fiscal_position_id:
                fiscal_position_id = Position.browse(fiscal_position_id)
                tax = fiscal_position_id.map_tax(tax, product, partner)
            taxes = tax.compute_all(self.price_unit * (1 - (self.discount or 0.0) / 100.0), self.subscription_id.currency_id, self.quantity, product, partner)['taxes']
            if taxes:
                val += taxes[0].get('amount', 0)
        return val
    
    def _prepare_invoice_line(self, fiscal_position):
        company = False
        if 'force_company' in self.env.context:
            company = self.env['res.company'].browse(self.env.context['force_company'])
        else:
            company = self.subscription_id.company_id
            self = self.with_context(force_company=company.id, company_id=company.id)

        account = self.product_id.property_account_income_id
        if not account:
            account = self.product_id.categ_id.property_account_income_categ_id
        account_id = fiscal_position.map_account(account).id

        tax = self.product_id.taxes_id.filtered(lambda r: r.company_id == company)
        tax = fiscal_position.map_tax(tax, product=self.product_id, partner=self.subscription_id.partner_id)
        return {
            'name': self.name,
            'account_id': account_id,
            'analytic_account_id': self.subscription_id.analytic_account_id.id,
            'subscription_id': self.subscription_id.id,
            'price_unit': self.price_unit or 0.0,
            'discount': self.discount,
            'quantity': self.quantity,
            'product_uom_id': self.uom_id.id,
            'product_id': self.product_id.id,
            'tax_ids': [(6, 0, tax.ids)],
            'analytic_tag_ids': [(6, 0, self.subscription_id.analytic_tag_ids.ids)]
        }

    def _prepare_invoice_lines(self, fiscal_position_id):
        fiscal_position = self.env['account.fiscal.position'].browse(fiscal_position_id)
        return [(0, 0, line._prepare_invoice_line(fiscal_position)) for line in self]

    def _prepare_renewal_sale_order_line_vals(self):
        self.ensure_one()
        return {
            'product_id': self.product_id.id,
            'name': self.product_id.product_tmpl_id.name,
            'subscription_id': self.subscription_id.id,
            'product_uom': self.uom_id.id,
            'product_uom_qty': self.quantity,
            'price_unit': self.price_unit,
            'discount': self.discount,
            }
