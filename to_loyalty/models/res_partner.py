from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty_point_ids = fields.One2many('loyalty.point', 'partner_id', string='Loyalty Points', readonly=True)
    loyalty_points = fields.Float(string='Total Loyalty Points',
                                  digits='Loyalty',
                                  compute='_compute_loyalty_points', store=True, index=True,
                                  help="The loyalty points the user won as part of a Loyalty Program")
    loyalty_id = fields.Many2one('loyalty.program', string='Loyalty Program', index=True)
    level_id = fields.Many2one('customer.level', string='Level', compute='_compute_customer_level', index=True,
                               tracking=True)

    @api.depends('loyalty_point_ids', 'loyalty_point_ids.points')
    def _compute_loyalty_points(self):
        for r in self:
            r.loyalty_points = sum(point_id.points for point_id in r.loyalty_point_ids)

    @api.depends('loyalty_points')
    def _compute_customer_level(self):
        Property = self.env['ir.property'].with_company(self.env.company)
        customerLevels = self.env['customer.level'].search([], order='points desc')
        for r in self:
            level_id = False
            for level in customerLevels:
                if r.loyalty_points >= level.points:
                    if not level_id or (level_id and level.points > level_id.points):
                        level_id = level
            if level_id:
                data = {
                    'level_id': level_id.id
                    }
                if level_id.property_sync_partner_pricelist:
                    if not level_id.property_pricelist_id:
                        # remove the old pricelist from customers to falback to the system default
                        property_ids = Property.search([
                            ('name', '=', 'property_product_pricelist'),
                            ('res_id', '=', '%s,%s' % (r._name, r.id))])
                        property_ids.sudo().unlink()
                    data['property_product_pricelist'] = level_id.property_pricelist_id and level_id.property_pricelist_id.id or False

                r.update(data)
            else:
                r.level_id = False

    def find_loyalty_program(self):
        self.ensure_one()
        return self.loyalty_id or self.commercial_partner_id.loyalty_id or False

