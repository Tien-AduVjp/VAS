from odoo import api, models, fields


class WarrantyClaim(models.Model):
    _inherit = "warranty.claim"

    repair_ids = fields.One2many('repair.order', 'warranty_claim_id', string="Repairs")
    repair_count = fields.Integer(string='Repair Count', compute="_compute_repair_count")

    @api.depends('repair_ids')
    def _compute_repair_count(self):
        for r in self:
            r.repair_count = len(r.repair_ids)

    def action_view_repair_history(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('to_repair_request_from_warranty.action_from_warranty_repair_history')
        action['context'] = {'search_default_warranty_claim_id': self.id, 'default_warranty_claim_id': self.id}
        return action

    def action_repair_request(self):
        action = self.env['ir.actions.act_window']._for_xml_id('repair.action_repair_order_tree')
        res = self.env.ref('repair.view_repair_order_form', False)
        action['views'] = [(res and res.id or False, 'form')]
        action['context'] = {'default_warranty_claim_id': self.id}
        return action

