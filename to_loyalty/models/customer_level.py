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
    partner_ids = fields.One2many('res.partner', string='Partners',
                                  compute='_count_partner_ids', compute_sudo=True,
                                  help="The partners who are classified at this level")
    partner_ids_count = fields.Integer(string='Partners Count',
                                       compute='_count_partner_ids', compute_sudo=True,
                                       )

    _sql_constraints = [
        ('points_uniq',
         'unique(points)',
         "The Minimum Points definition must be unique!"),

        ('name_unique',
         'UNIQUE(name)',
         "The Name must be unique!"),
    ]

    def _count_partner_ids(self):
        partners = self.env['res.partner'].search([])
        for r in self:
            partners_temp = partners.filtered(lambda p: p.level_id.id == r.id)
            r.partner_ids = partners_temp
            r.partner_ids_count = len(partners_temp)

    def get_next_level(self):
        return self.search([('points', '>', self.points)], limit=1)

    def sync_partner_pricelist(self):
        Property = self.env['ir.property'].with_company(self.env.company)
        partners = self.env['res.partner'].with_context(active_test=False).search([])
        for r in self.filtered(lambda l: l.property_sync_partner_pricelist):
            partners = partners.filtered(lambda p: p.level_id.id == r.id)
            if partners:
                if not r.property_pricelist_id:
                    # remove the old pricelist from customers to falback to the system default
                    res_id_list = ['%s,%s' % (partners._name, partner.id) for partner in partners]
                    property_ids = Property.search([
                        ('name', '=', 'property_product_pricelist'),
                        ('res_id', 'in', res_id_list)])
                    property_ids.sudo().unlink()
                partners.write({'property_product_pricelist': r.property_pricelist_id and r.property_pricelist_id.id or False})

    def write(self, vals):
        res = super(CustomerLevel, self).write(vals)
        if 'property_pricelist_id' in vals:
            self.sync_partner_pricelist()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        level_ids = super(CustomerLevel, self).create(vals_list)
        level_ids.sync_partner_pricelist()
        return level_ids

    def action_view_partners(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_partner_form')

        # get rid of default context
        action['context'] = {}

        # choose the view_mode accordingly
        if self.partner_ids_count == 1:
            res = self.env.ref('base.view_partner_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.partner_ids.id
        elif self.partner_ids_count > 1:
            partners = self.env['res.partner'].search([])
            partners = partners.filtered(lambda p: p.level_id.id == self.id)
            action['domain'] = "[('id', 'in', %s)]" % partners.ids
        return action

