from odoo import fields, models


class MrpProductForecast(models.Model):
    _name = 'mrp.product.forecast'
    _description = 'Product Forecast'
    _order = 'date'

    production_schedule_id = fields.Many2one('mrp.production.schedule', string='MPS', required=True, ondelete='cascade')
    date = fields.Date('Date', required=True)
    forecast_qty = fields.Float('Demand Forecast')
    replenish_qty = fields.Float('To Replenish Quantity')
    replenish_qty_updated = fields.Boolean()
    procurement_launched = fields.Boolean()
