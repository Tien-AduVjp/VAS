from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_foreign_trade_partner = fields.Boolean(string="Foreign Trade Partner", company_dependent=True,
                                           help='If checked, sale/purchase made with this partner will be considered as foreign trade.'
                                           ' Hence, activate custom clearance procedure.')

    same_company_country = fields.Boolean(string="Same Company Country",
                                     compute='_check_same_country',
                                     help="Used to check readonly condition on form")

    @api.model
    def update_existing_foreign_partners(self):
        Parner = self.env['res.partner']
        companies = self.env['res.company'].search([])
        export_customer_loc_id = self.env.ref('viin_foreign_trade.to_stock_location_customers_export')
        for company in companies:
            company_partners = Parner.search([('company_id', '=', company.id)])
            for partner in company_partners:
                if partner.country_id.id != company.country_id.id:
                    partner.write({'property_foreign_trade_partner':True, 'property_stock_customer': export_customer_loc_id.id})

    @api.depends('country_id', 'company_id.country_id', 'commercial_partner_id')
    def _check_same_country(self):
        for r in self:
            partner_country = r.commercial_partner_id.country_id or r.country_id
            company = r.commercial_partner_id.company_id or r.company_id or self.env.company
            if partner_country and company and company.country_id == partner_country:
                r.same_company_country = True
            else:
                r.same_company_country = False

    @api.onchange('country_id', 'company_id')
    def _onchange_country_company(self):
        self._check_same_country()
        last_property_foreign_trade_partner = self._origin.property_foreign_trade_partner
        if self.country_id:
            if not self.same_company_country:
                self.property_foreign_trade_partner = True
            else:
                self.property_foreign_trade_partner = False
        else:
            self.property_foreign_trade_partner = last_property_foreign_trade_partner

    @api.onchange('property_foreign_trade_partner')
    def _onchange_property_foreign_trade_partner(self):

        self.property_stock_customer = self.property_foreign_trade_partner \
            and self.env.ref('viin_foreign_trade.to_stock_location_customers_export') \
            or self.env.ref('stock.stock_location_customers')

    @api.model_create_multi
    def create(self, vals_list):
        partners = super(ResPartner, self).create(vals_list)
        export_customer_loc_id = self.env.ref('viin_foreign_trade.to_stock_location_customers_export')
        for partner in partners.filtered(lambda p: p.country_id and p.company_id.country_id):
            if partner.country_id.id != partner.company_id.country_id.id:
                partner.write({
                    'property_foreign_trade_partner': True,
                    'property_stock_customer': export_customer_loc_id.id
                    })
        return partners

    def write(self, vals):
        country_id = vals.get('country_id', False)
        company_id = vals.get('company_id', False)
        export_customer_loc_id = self.env.ref('viin_foreign_trade.to_stock_location_customers_export')
        if country_id and company_id:
            company = self.env['res.company'].browse(company_id)
            if country_id != company.country_id.id:
                self.property_foreign_trade_partner = True
                self.property_stock_customer = export_customer_loc_id.id
        elif country_id:
            for record in self:
                if country_id != record.company_id.country_id.id:
                    record.property_foreign_trade_partner = True
        elif company_id:
            company = self.env['res.company'].browse(company_id)
            for record in self:
                if record.country_id.id != company.country_id.id:
                    record.property_foreign_trade_partner = True

        return super(ResPartner, self).write(vals)
