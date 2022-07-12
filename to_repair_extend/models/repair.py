from odoo import fields, models


class Repair(models.Model):
    _inherit = 'repair.order'
    
    repair_date = fields.Date(string='Repair date', default=fields.Date.today)
    supervisor_id = fields.Many2one("res.users", string="Supervisor")  # TODO 14.0: Should remove this, also on repair report too
    feedback = fields.Text("Customer's Feedback")
    forecast = fields.Text("Forecast")
