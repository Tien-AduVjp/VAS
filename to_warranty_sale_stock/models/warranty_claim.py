from odoo import api, models


class WarrantyClaim(models.Model):
    _inherit = 'warranty.claim'

    @api.onchange('lot_id')
    def _onchange_lot_id_for_sale(self):
        res = {}
        if self.lot_id:
            self.sale_order_id = self.lot_id.sale_order_id
            self.partner_id = self.sale_order_id.partner_id
        else:
            self.sale_order_id = False
            self.partner_id = False
            self.warranty_start_date = False
            self.warranty_period = False
            self.warranty_expiration_date = False
        return res

    @api.depends('product_id')
    def _compute_available_so_ids(self):
        super(WarrantyClaim, self)._compute_available_so_ids()
        for r in self:
            if r.lot_id and r.lot_id.sale_order_id:
                r.available_so_ids = r.lot_id.sale_order_id

    @api.depends('lot_id', 'lot_id.warranty_start_date', 'sale_order_id')
    def _compute_warranty_start_date(self):
        super(WarrantyClaim, self)._compute_warranty_start_date()
        for r in self:
            if r.type == 'customer':
                if r.lot_id:
                    r.warranty_start_date = r.lot_id.warranty_start_date

    @api.depends('product_id', 'type', 'sale_order_id')
    def _compute_warranty_claim_policy_ids(self):
        super(WarrantyClaim, self)._compute_warranty_claim_policy_ids()
        for r in self:
            warranty_claim_policies = self.env['warranty.claim.policy']

            if r.type == 'customer':
                if r.lot_id:
                    warranty_claim_policy_ids = r.lot_id.mapped('warranty_claim_policy_ids').filtered(lambda l: l.apply_to == 'sale')
                    for warranty_claim_policy in warranty_claim_policy_ids:
                        warranty_claim_policies += warranty_claim_policies.new(warranty_claim_policy._prepare_warranty_claim_policy_on_lot_data())
                    r.warranty_claim_policy_ids = warranty_claim_policies
