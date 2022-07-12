from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class WarrantyClaim(models.Model):
    _inherit = "warranty.claim"

    lot_id = fields.Many2one('stock.production.lot', string='Lots/ Serial Numbers', readonly=False, states={'investigation': [('readonly', True)],
                                                                                                            'disclaimed': [('readonly', True)],
                                                                                                            'confirmed': [('readonly', True)],
                                                                                                            'done': [('readonly', True)],
                                                                                                            'cancelled': [('readonly', True)]})
    available_product_ids = fields.Many2many('product.product', compute='_compute_available_product_ids', string='Available Product',
                                             help="Technical field to filter product based on selected lot")
    product_id = fields.Many2one(compute='_compute_product_id', store=True, tracking=True, 
                                 readonly=False, copy=True,
                                 domain="[('id', 'in', available_product_ids)]")

    @api.constrains('lot_id', 'product_id')
    def _check_constrains_product_and_lot(self):
        for r in self:
            if r.lot_id and r.product_id != r.lot_id.product_id:
                raise ValidationError(_("Product and Lot serial must be unique"))

    @api.onchange('type')
    def _onchange_lot_and_type(self):
        res = {}
        if self.lot_id:
            self.product_id = self.lot_id.product_id
            warranty_claim_policy = self.env['warranty.claim.policy']
            apply_to = None
            if self.type == 'customer':
                apply_to = 'sale'
            elif self.type == 'vendor':
                apply_to = 'purchase'
            warranty_claim_policy_ids = self.lot_id.mapped('warranty_claim_policy_ids').filtered(lambda l: l.apply_to == apply_to)
            for warranty_claim_policy_id in warranty_claim_policy_ids:
                warranty_claim_policy += warranty_claim_policy.new(warranty_claim_policy_id._prepare_warranty_claim_policy_on_lot_data())
            self.warranty_claim_policy_ids = warranty_claim_policy
        return res
    
    @api.depends('lot_id')
    def _compute_available_product_ids(self):
        for r in self:
            if r.lot_id:
                r.available_product_ids = self.env['product.product'].search([('id', '=', r.lot_id.product_id.id)])
            else:
                r.available_product_ids = self.env['product.product'].search([])

    @api.depends('lot_id')
    def _compute_product_id(self):
        for r in self:
            r.product_id = r.lot_id and r.lot_id.product_id or False

    @api.depends('lot_id', 'lot_id.warranty_start_date')
    def _compute_warranty_start_date(self):
        super(WarrantyClaim, self)._compute_warranty_start_date()
        for r in self:
            if r.lot_id:
                r.warranty_start_date = r.lot_id.warranty_start_date

    @api.depends('lot_id', 'lot_id.warranty_period')
    def _compute_warranty_period(self):
        super(WarrantyClaim, self)._compute_warranty_period()
        for r in self:
            if r.lot_id:
                r.warranty_period = r.lot_id.warranty_period

    @api.depends('lot_id')
    def _compute_warranty_expiration_date(self):
        super(WarrantyClaim, self)._compute_warranty_expiration_date()
        for r in self:
            if r.lot_id:
                r.warranty_expiration_date = r.lot_id.warranty_expiration_date

    @api.depends('product_id', 'type')
    def _compute_warranty_claim_policy_ids(self):
        for r in self:
            if r.lot_id:
                warranty_claim_policy = self.env['warranty.claim.policy']
                apply_to = None
                if r.type == 'customer':
                    apply_to = 'sale'
                elif r.type == 'vendor':
                    apply_to = 'purchase'
                warranty_claim_policy_ids = r.lot_id.warranty_claim_policy_ids.filtered(lambda l: l.apply_to == apply_to)
                for warranty_claim_policy_id in warranty_claim_policy_ids:
                    warranty_claim_policy += warranty_claim_policy.new(warranty_claim_policy_id._prepare_warranty_claim_policy_on_lot_data())
                r.warranty_claim_policy_ids = warranty_claim_policy
            else:
                super(WarrantyClaim, r)._compute_warranty_claim_policy_ids()

    def action_confirm(self):
        for r in self:
            if r.lot_id and not r.warranty_expiration_date:
                raise ValidationError(_("Cannot confirm Warranty Claims which doesn't have Warranty Expiration Date, please re-check on Lots/ Serial Numbers: %s") % r.lot_id.name)
        return super(WarrantyClaim, self).action_confirm()
