from odoo import models, _
from odoo.exceptions import ValidationError


class AbstractCustomDeclaration(models.AbstractModel):
    _inherit = 'abstract.custom.declaration'

    def _prepare_landed_cost_data(self):
        account_journal_id = self.company_id.landed_cost_journal_id
        if not account_journal_id: 
            raise ValidationError(_('There is no account journal defined on the Landed Cost Journal for current company.'))
        return {
                'date': self.clearance_date,
                'picking_ids': [(6, 0, [self.stock_picking_id.id])],
                'account_journal_id': account_journal_id.id,
            }
    
    def action_confirm(self):
        super(AbstractCustomDeclaration, self).action_confirm()
        if self._should_create_landed_cost():
            cost_lines = self.env['stock.landed.cost.lines']
            valuation_ajustment_lines = self.env['stock.valuation.adjustment.lines']
            for r in self:
                if r.tax_line_ids:
                    landed_cost = self.env['stock.landed.cost'].create(r._prepare_landed_cost_data())
                    for line in r.tax_line_ids.filtered(lambda x: not x.is_vat):
                        cost_line = cost_lines.create(line._prepare_landed_cost_line_data(landed_cost))
                        valuation_ajustment_lines.create(line._prepare_landed_cost_adjustment_line_data(cost_line))
                
    def action_cancel(self):
        posted_laned_cost = self.mapped('landed_cost_ids').filtered(lambda x: x.state == 'done')
        if posted_laned_cost:
            raise ValidationError(_('Can not cancel this document while it has some posted landed cost.'))
        self.mapped('landed_cost_ids').unlink()
        super(AbstractCustomDeclaration, self).action_cancel()
        
    def _should_create_landed_cost(self):
        return False
