import threading

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    foreign_trade = fields.Boolean(string="Foreign Import", compute='_compute_foreign_trade', store=True)
    custom_declaration_ids = fields.One2many('custom.declaration.import', 'purchase_order_id', string="Custom Clearance Request", readonly=True)
    custom_dec_count = fields.Integer(string="# of Custom Declaration Documents", compute='_compute_custom_dec_count')
    available_pk_type_ids = fields.Many2many('stock.picking.type', compute='_compute_available_pk_type_ids', 
                                             string='Available Transfer Types',
                                             help="Technical field to filter transfer types based on foreign import")

    @api.model
    def update_existing_orders(self):
        """
        Method to be called upon first installation
        """
        orders = self.search([('partner_id.property_foreign_trade_partner', '=', True)])
        orders.write({'foreign_trade': True})
        company_ids = self.env['res.company'].search([])
        for company_id in company_ids:
            import_picking_type_id = self.env['stock.picking.type'].search([
                ('warehouse_id.company_id', '=', company_id.id),
                ('is_custom_clearance', '=', True),
                ('custom_clearance_type', '=', 'import')], limit=1)
            if import_picking_type_id:
                unconfirmed_orders = orders.filtered(lambda r: r.state not in ('purchase', 'done') \
                                                     and r.company_id.id == company_id.id \
                                                     and r.picking_type_id.id != import_picking_type_id.id)
                unconfirmed_orders.write({'picking_type_id': import_picking_type_id.id})
    
    @api.depends('foreign_trade')
    def _compute_available_pk_type_ids(self):
        for r in self:
            pk_type_domain = [('code','=','incoming'), '|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', r.company_id.id)]
            if r.foreign_trade:
                additional_domain = [('is_foreign_trade', '=', True)]
                pk_type_domain = expression.AND([pk_type_domain, additional_domain])
            else:
                additional_domain = [('is_foreign_trade', '=', False)]
                pk_type_domain = expression.AND([pk_type_domain, additional_domain])

            r.available_pk_type_ids = self.env['stock.picking.type'].search(pk_type_domain)
    
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
        custom_dec_data = self.env['custom.declaration.import'].sudo().read_group([('purchase_order_id', 'in', self.ids)], ['purchase_order_id'], ['purchase_order_id'])
        mapped_data = dict([(dict_data['purchase_order_id'][0], dict_data['purchase_order_id_count']) for dict_data in custom_dec_data])
        for r in self:
            r.custom_dec_count = mapped_data.get(r.id, 0)

    @api.onchange('foreign_trade')
    def onchange_foreign_trade(self):
        pk_type_domain = [('code','=','incoming'), '|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', self.company_id.id)]
        if self.foreign_trade:
            additional_domain = [('is_foreign_trade', '=', True)]
            pk_type_domain = expression.AND([pk_type_domain, additional_domain])

            picking_type_id = self.env['stock.picking.type'].search(pk_type_domain, limit=1)
            if not picking_type_id:
                test_mode = getattr(threading.currentThread(), 'testing', False)
                if not test_mode:
                    raise ValidationError(_('Could not find a right picking type for Foreign Import purchase.'
                                            ' You must have one, otherwise, foreign purchase may raise unexpected results.'
                                            ' You may need to enable Foreign Import feature for at least one warehouse in'
                                            ' you system.'))
                picking_type_id = self._default_picking_type()
            self.picking_type_id = picking_type_id
        else:
            self.picking_type_id = self._default_picking_type()

    def action_view_custom_declarations(self):
        self.ensure_one()
        custom_declaration_ids = self.custom_declaration_ids
        action = self.env.ref('to_foreign_trade.custom_declaration_import_action')
        result = action.read()[0]
        # override the context to get rid of the default filtering
        result['context'] = {}
        # choose the view_mode accordingly
        if len(custom_declaration_ids) != 1:
            result['domain'] = [('purchase_order_id', '=', self.id)]

        elif len(custom_declaration_ids) == 1:
            res = self.env.ref('to_foreign_trade.custom_declaration_import_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = custom_declaration_ids.id
        return result
