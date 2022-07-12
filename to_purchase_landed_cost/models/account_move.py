from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    # TODOS: remove in Odoo 14, use landed_costs_visible instead
    is_landed_costs_bill = fields.Boolean(string='Is Landed Cost Bill', compute='_compute_is_landed_costs_bill',
                                      help="To indicate of the invoice contains a line as landed costs for some purchase orders",
                                      store=True)

    landed_costs_count = fields.Integer(string='Landed Costs Count', compute='_compute_landed_costs_count')

    def _compute_landed_costs_count(self):
        for r in self:
            r.landed_costs_count = len(r.landed_costs_ids)

    @api.depends('line_ids', 'line_ids.landed_cost_for_po_ids', 'line_ids.product_id')
    def _compute_is_landed_costs_bill(self):
        # line.product_id.product_tmpl_id.landed_cost_ok
        for r in self:
            if r.line_ids.mapped('landed_cost_for_po_ids') or any(product.product_tmpl_id.landed_cost_ok for product in r.line_ids.mapped('product_id')):
                r.is_landed_costs_bill = True
            else:
                r.is_landed_costs_bill = False
