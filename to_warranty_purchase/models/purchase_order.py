from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    warranty_claim_ids = fields.One2many('warranty.claim', 'purchase_order_id', string='Warranty Claims')
    warranty_claim_count = fields.Integer(compute='_compute_warranty_claim_count', string='Warranty Claim count', compute_sudo=True)

    def button_confirm(self):
        for line in self.mapped('order_line'):
            line.warranty_policy_ids = line.mapped('product_id.warranty_policy_ids').filtered(lambda x: x.apply_to == 'purchase')
        return super(PurchaseOrder, self).button_confirm()

    @api.depends('warranty_claim_ids')
    def _compute_warranty_claim_count(self):
        for r in self:
            r.warranty_claim_count = len(r.warranty_claim_ids)

    def action_warranty_claim(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id('to_warranty_management.action_warranty_claim_purchase')
        result['context'] = {'default_purchase_order_id': self.id, 'default_type':'vendor', 'default_partner_id' : self.partner_id}
        warranty_claims = self.warranty_claim_ids
        if not warranty_claims or len(warranty_claims) > 1:
            result['domain'] = "[('id','in',%s)]" % (warranty_claims.ids)
        elif len(warranty_claims) == 1:
            res = self.env.ref('to_warranty_management.warranty_claim_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = warranty_claims.id
        return result
