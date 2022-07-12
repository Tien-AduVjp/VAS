from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class WarrantyClaim(models.Model):
    _inherit = "warranty.claim"

    available_so_ids = fields.Many2many('sale.order', compute='_compute_available_so_ids', string='Available SO',
                                        help="Technical field to filter sale order based on selected product")
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=False, 
                                    states={'investigation': [('readonly', True)],
                                            'disclaimed': [('readonly', True)],
                                            'confirmed': [('readonly', True)],
                                            'done': [('readonly', True)],
                                            'cancelled': [('readonly', True)]},
                                    domain="[('id', 'in', available_so_ids)]")
    partner_id = fields.Many2one(compute='_compute_warranty_claim_policy_ids', store=True, copy=True)
    
    @api.depends('product_id')
    def _compute_available_so_ids(self):
        for r in self:
            if r.product_id:
                r.available_so_ids = self.env['sale.order'].search([('order_line.product_id', '=', r.product_id.id), ('state', 'in', ('sale', 'done'))])
            else:
                r.available_so_ids = self.env['sale.order'].search([('state', 'in', ('sale', 'done'))])
    
    @api.depends('sale_order_id')
    def _compute_warranty_start_date(self):
        super(WarrantyClaim, self)._compute_warranty_start_date()
        for r in self:
            if r.type == 'customer' and r.sale_order_id and r.sale_order_id.date_order:
                r.warranty_start_date = r.sale_order_id.date_order.date()
    
    @api.depends('product_id', 'type', 'sale_order_id')
    def _compute_warranty_claim_policy_ids(self):
        super(WarrantyClaim, self)._compute_warranty_claim_policy_ids()
        for r in self:
            warranty_claim_policy_ids = r.env['warranty.claim.policy']
            if r.type == 'customer' and r.sale_order_id:
                warranty_policy_ids = r.sale_order_id.order_line.filtered(lambda line: line.product_id == self.product_id).mapped('warranty_policy_ids')
                if warranty_policy_ids:
                    for warranty_policy_id in warranty_policy_ids:
                        warranty_claim_policy_ids += warranty_claim_policy_ids.new(warranty_policy_id._prepare_warranty_claim_policy_data())
                r.warranty_claim_policy_ids = warranty_claim_policy_ids
                r.partner_id = r.sale_order_id.partner_id
                
    def action_investigation(self):
        for r in self:
            if r.product_id and r.sale_order_id:
                if r.product_id not in r.sale_order_id.order_line.product_id:
                    raise ValidationError(_("You cannot investigate a warranty claim, which has product and sale order are not consistent."))
        return super(WarrantyClaim, self).action_investigation()
