from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _make_po_get_domain(self, company_id, values, partner):
        """
        Override to avoid merging two Requests for Quotation for the same Master Production Schedule replenishment.
        """
        domain = super(StockRule, self)._make_po_get_domain(company_id, values, partner)
        if self.env.context.get('skip_lead_time') and values.get('date_planned'):
            domain += (('date_planned_mps', '=', values['date_planned']),)
        return domain
