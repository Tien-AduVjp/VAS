from odoo import api, models


class WarrantyClaim(models.Model):
    _inherit = "warranty.claim"

    @api.onchange('lot_id')
    def _onchange_lot_id_for_purchase(self):
        res = {}
        if self.lot_id:
            self.purchase_order_id = self.lot_id.purchase_order_id
            self.partner_id = self.purchase_order_id.partner_id
        else:
            self.purchase_order_id = False
            self.partner_id = False
            self.warranty_start_date = False
            self.warranty_period = False
            self.warranty_expiration_date = False
        return res
    
    @api.depends('product_id')
    def _compute_available_po_ids(self):
        super(WarrantyClaim, self)._compute_available_po_ids()
        for r in self:
            if r.lot_id and r.lot_id.purchase_order_id:
                r.available_po_ids = r.lot_id.purchase_order_id
    
    @api.depends('lot_id', 'lot_id.warranty_start_date', 'purchase_order_id')
    def _compute_warranty_start_date(self):
        super(WarrantyClaim, self)._compute_warranty_start_date()
        for r in self:
            if r.type == 'vendor':
                if r.lot_id:
                    r.warranty_start_date = r.lot_id.warranty_start_date

    @api.depends('product_id', 'type', 'purchase_order_id')
    def _compute_warranty_claim_policy_ids(self):
        super(WarrantyClaim, self)._compute_warranty_claim_policy_ids()
        for r in self:
            warranty_claim_policy = self.env['warranty.claim.policy']
            
            if r.type == 'vendor':
                if r.lot_id:
                    warranty_claim_policy_ids = r.lot_id.mapped('warranty_claim_policy_ids').filtered(lambda l: l.apply_to == 'purchase')
                    for warranty_claim_policy_id in warranty_claim_policy_ids:
                        warranty_claim_policy += warranty_claim_policy.new(warranty_claim_policy_id._prepare_warranty_claim_policy_on_lot_data())
                    r.warranty_claim_policy_ids = warranty_claim_policy
