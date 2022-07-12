from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    foreign_trade = fields.Boolean(string="Foreign Export", compute='_compute_foreign_trade', store=True)
    custom_declaration_ids = fields.One2many('custom.declaration.export', 'sale_order_id', string="Custom Clearance Request", readonly=True,
        groups="stock.group_stock_user,to_foreign_trade.group_foreign_trade_user")
    custom_dec_count = fields.Integer(string="# of Custom Clearance Request", compute='_compute_custom_dec_count')

    @api.model
    def update_existing_orders(self):
        """
        Method to be called upon first installation
        """
        orders = self.search([('partner_id.property_foreign_trade_partner', '=', True)])
        orders.write({'foreign_trade': True})
        
    
    @api.depends('partner_id.property_foreign_trade_partner', 'partner_id.country_id', 'company_id.country_id')
    def _compute_foreign_trade(self):
        for r in self:
            if r.partner_id:
                if r.partner_id.property_foreign_trade_partner:
                    r.foreign_trade = True
                else:
                    if r.partner_id.country_id and r.partner_id.country_id != r.company_id.country_id:
                        r.foreign_trade = True
                    else:
                        r.foreign_trade = False
            else:
                r.foreign_trade = False

    @api.depends('custom_declaration_ids')
    def _compute_custom_dec_count(self):
        # we need sudo as sales person may not have read access to custom.declaration.export
        custom_dec_data = self.env['custom.declaration.export'].sudo().read_group([('sale_order_id', 'in', self.ids)], ['sale_order_id'], ['sale_order_id'])
        mapped_data = dict([(dict_data['sale_order_id'][0], dict_data['sale_order_id_count']) for dict_data in custom_dec_data])
        for r in self:
            r.custom_dec_count = mapped_data.get(r.id, 0)

    def action_view_custom_declarations(self):
        self.ensure_one()
        custom_declaration_ids = self.custom_declaration_ids
        action = self.env.ref('to_foreign_trade.custom_declaration_export_action')
        result = action.read()[0]
        # override the context to get rid of the default filtering
        result['context'] = {}
        # choose the view_mode accordingly
        if len(custom_declaration_ids) != 1:
            result['domain'] = "[('sale_order_id', '=', " + str(self.id) + ")]"
        elif len(custom_declaration_ids) == 1:
            res = self.env.ref('to_foreign_trade.custom_declaration_export_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = custom_declaration_ids.id
        return result
