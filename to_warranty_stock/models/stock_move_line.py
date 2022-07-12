from odoo import models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _get_warranty_policy_ids(self):
        if self.lot_id:
            return self.lot_id.product_id.mapped('warranty_policy_ids')

    def _action_done(self):
        super(StockMoveLine, self)._action_done()
        WarrantyClaimPolicy = self.env['warranty.claim.policy']
        for ml in self.exists():
            if ml.lot_id:
                warranty_policies = ml._get_warranty_policy_ids()
                for warranty_policy in warranty_policies:
                    existed_warranty_claim_policy = ml.lot_id.warranty_claim_policy_ids.filtered(lambda \
                                x: x.product_milestone_id == warranty_policy.product_milestone_id \
                                and x.apply_to == warranty_policy.apply_to)
                    if existed_warranty_claim_policy:
                        continue

                    vals = warranty_policy._prepare_warranty_claim_policy_data()
                    vals.update({'stock_production_lot_id': ml.lot_id.id})
                    WarrantyClaimPolicy.create(vals)
