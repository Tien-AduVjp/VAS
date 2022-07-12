from odoo import api, fields, models
from odoo.tools import float_is_zero


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.depends('company_id', 'location_id', 'owner_id', 'product_id', 'quantity')
    def _compute_value(self):
        """ For specific identification valuation, compute the current accounting
        valuation of the quants by summing the valuation layers's remaining value.
        """
        super(StockQuant, self)._compute_value()

        spec_quants = self.filtered(lambda r: r.location_id and r.product_id.cost_method == 'specific_identification')
        if spec_quants:
            company_id = self.env.context.get('force_company', self.env.company.id)
            domain = [
                ('product_id', 'in', spec_quants.product_id.ids),
                ('lot_id', 'in', spec_quants.lot_id.ids),
                ('company_id', '=', company_id),
            ]
            if self.env.context.get('to_date'):
                to_date = fields.Datetime.to_datetime(self.env.context['to_date'])
                domain.append(('create_date', '<=', to_date))
            layers = self.env['stock.valuation.layer'].search(domain)
            
            if layers:
                for r in spec_quants:
                    layers_temp = layers.filtered(lambda l: l.product_id == r.product_id and l.lot_id == r.lot_id)
                    if layers_temp:
                        r.value = sum([l.remaining_value for l in layers_temp])
                        layers -= layers_temp
