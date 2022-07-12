from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    landed_costs_count = fields.Integer(string='Landed Costs Count', compute='_compute_landed_costs_count')

    def _compute_landed_costs_count(self):
        for r in self:
            r.landed_costs_count = len(r.landed_costs_ids)

    def button_create_landed_costs(self):
        """Fill transfer of purchase order to landed cost."""
        action = super(AccountInvoice, self).button_create_landed_costs()

        landed_cost = self.env['stock.landed.cost'].browse(action['res_id'])
        landed_costs_lines = self.line_ids.filtered(lambda line: line.is_landed_costs_line)

        po = (landed_costs_lines.purchase_order_id | landed_costs_lines.purchase_order_id.landed_costs_for_po_ids)
        pickings = po.picking_ids.filtered(lambda p: p in landed_cost.allowed_picking_ids)

        landed_cost.write({'picking_ids': [(4, p.id) for p in pickings]})

        return action
