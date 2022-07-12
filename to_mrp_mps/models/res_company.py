from odoo import fields, models
from odoo.tools.date_utils import start_of, end_of, add


class Company(models.Model):
    _inherit = 'res.company'

    manufacturing_period = fields.Selection([
        ('month', 'Monthly'),
        ('week', 'Weekly'),
        ('day', 'Daily')], string='Manufacturing Period',
        default='week', required=True,
        help="Default time ranges in Master Production Schedule report.")
    manufacturing_period_to_display = fields.Integer(string='Manufacturing Periods to Display',
                                                     help="Number of period columns to display "
                                                          "in Master Production Schedule report", default=12)

    mrp_mps_show_starting_inventory = fields.Boolean(string='Show Starting Inventory', default=True)
    mrp_mps_show_demand_forecast = fields.Boolean(string='Show Demand Forecast', default=True)
    mrp_mps_show_actual_demand = fields.Boolean(string='Show Actual Demand', default=False)
    mrp_mps_show_indirect_demand = fields.Boolean(string='Show Indirect Demand', default=True)
    mrp_mps_show_to_replenish = fields.Boolean(string='Show To Replenish', default=True)
    mrp_mps_show_actual_replenishment = fields.Boolean(string='Show Actual Replenishment', default=False)
    mrp_mps_show_safety_stock = fields.Boolean(string='Show Safety Stock', default=True)
    mrp_mps_show_available_to_promise = fields.Boolean(string='Show Available to Promise', default=False)

    def _get_mps_display_groups(self):
        self.ensure_one()
        return self.read([
            'mrp_mps_show_starting_inventory',
            'mrp_mps_show_demand_forecast',
            'mrp_mps_show_indirect_demand',
            'mrp_mps_show_actual_demand',
            'mrp_mps_show_to_replenish',
            'mrp_mps_show_actual_replenishment',
            'mrp_mps_show_safety_stock',
            'mrp_mps_show_available_to_promise',
        ])

    def _get_mps_date_range(self):
        self.ensure_one()
        date_range = []
        date_start = start_of(fields.Date.today(), self.manufacturing_period)
        for columns in range(self.manufacturing_period_to_display):
            date_end = end_of(date_start, self.manufacturing_period)
            date_range.append((date_start, date_end))
            date_start = add(date_end, days=1)
        return date_range
