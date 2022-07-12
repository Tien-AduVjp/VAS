from odoo import fields, models, api


class Repair(models.Model):
    _inherit = 'repair.order'

    warranty_claim_id = fields.Many2one('warranty.claim', string="Warranty Claim")
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        """
        Implement this method to keep guarantee_limit based on warranty expiration date of selected warranty claim when change product
        """
        super(Repair, self).onchange_product_id()
        if self.warranty_claim_id:
            self.guarantee_limit = self.warranty_claim_id.warranty_expiration_date

    @api.onchange('warranty_claim_id')
    def _onchange_warranty_claim_id(self):
        if self.warranty_claim_id:
            self.guarantee_limit = self.warranty_claim_id.warranty_expiration_date
            self.product_id = self.warranty_claim_id.product_id.id
            self.product_uom = self.product_id.uom_id
            self.lot_id = self.warranty_claim_id.lot_id.id
            self.partner_id = self.warranty_claim_id.partner_id.id
        else:
            self.guarantee_limit = self._origin.guarantee_limit or self.guarantee_limit
            self.product_id = self._origin.product_id.id or self.product_id.id
            self.product_uom = self.product_id.uom_id
            self.lot_id = self._origin.lot_id.id or self.lot_id.id
            self.partner_id = self._origin.partner_id.id or self.partner_id.id
