from odoo import fields, models, api


class CustomerLevel(models.Model):
    _name = 'customer.level'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Customer Level'
    _order = 'points'

    name = fields.Char(string='Name', required=True, tracking=True,
                       help="Identification for the customer level. E.g. Silver, Gold, etc")
    points = fields.Float(string='Minimum Points', digits='Loyalty', required=True, tracking=True,
                          help='The minimum amount of points for this level at which the customer will be promoted to this level')
    property_pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', tracking=True,
                                            company_dependent=True,
                                            help="The specific pricelist that will be applied to the customers of this level."
                                            " Leave this empty if you want to disable this feature for customers of this level.")
    property_sync_partner_pricelist = fields.Boolean(string="Customer's Pricelist Sync.", company_dependent=True,
                                                       help="If checked, this will synchronize partner pricelist also. In case no pricelist specified"
                                                       " for the level, default pricelist will be written on the corresponding partners.")
    partner_ids = fields.One2many('res.partner', 'level_id', string='Partners',
                                  help="The partners who are classified at this level")
    partner_ids_count = fields.Integer(string='Partners Count', compute='_count_partner_ids')

    _sql_constraints = [
        ('points_uniq',
         'unique(points)',
         "The Minimum Points definition must be unique!"),

        ('name_unique',
         'UNIQUE(name)',
         "The Name must be unique!"),
    ]

    def _count_partner_ids(self):
        partners_data = self.env['res.partner'].read_group([('level_id', 'in', self.ids)], ['level_id'], ['level_id'])
        mapped_data = dict([(dict_data['level_id'][0], dict_data['level_id_count']) for dict_data in partners_data])
        for r in self:
            r.partner_ids_count = mapped_data.get(r.id, 0)

    def get_next_level(self):
        return self.search([('points', '>', self.points)], limit=1)

    def _associate_partners(self):
        self.ensure_one()
        domain = [
            '|', ('level_id', '!=', self.id), ('level_id', '=', False),
            ('loyalty_points', '>=', self.points)]
        next_level_id = self.get_next_level()
        if next_level_id:
            domain += [('loyalty_points', '<', next_level_id.points)]

        partner_ids = self.env['res.partner'].with_context(active_test=False).search(domain)
        if partner_ids:
            partner_ids.write({'level_id': self.id})

    def associate_partners(self):
        for r in self:
            r._associate_partners()

    def sync_partner_pricelist(self):
        Property = self.env['ir.property'].with_context(force_company=self.env.company.id)
        for r in self.filtered(lambda l: l.property_sync_partner_pricelist):
            partner_ids = self.env['res.partner'].with_context(active_test=False).search([('level_id', '=', r.id)])
            if partner_ids:
                if not r.property_pricelist_id:
                    # remove the old pricelist from customers to falback to the system default
                    res_id_list = ['%s,%s' % (partner_ids._name, partner_id.id) for partner_id in partner_ids]
                    property_ids = Property.search([
                        ('name', '=', 'property_product_pricelist'),
                        ('res_id', 'in', res_id_list)])
                    property_ids.sudo().unlink()
                partner_ids.write({'property_product_pricelist': r.property_pricelist_id and r.property_pricelist_id.id or False})

    def write(self, vals):
        should_associate_partners = 'points' in vals
        should_sync_partner_pricelist = 'property_pricelist_id' in vals
        res = super(CustomerLevel, self).write(vals)
        if should_associate_partners:
            self.associate_partners()
        if should_sync_partner_pricelist:
            self.sync_partner_pricelist()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        level_ids = super(CustomerLevel, self).create(vals_list)
        level_ids.associate_partners()
        level_ids.sync_partner_pricelist()
        return level_ids

    def action_view_partners(self):
        self.ensure_one()
        action = self.env.ref('base.action_partner_form')
        result = action.read()[0]

        # get rid of default context
        result['context'] = {}

        # choose the view_mode accordingly
        partner_ids_count = self.partner_ids_count
        if partner_ids_count != 1:
            result['domain'] = "[('level_id', 'in', %s)]" % self.ids
        elif partner_ids_count == 1:
            res = self.env.ref('base.view_partner_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.partner_ids.id
        return result

