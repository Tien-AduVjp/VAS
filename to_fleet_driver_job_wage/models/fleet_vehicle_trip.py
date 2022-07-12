from odoo import models, fields, api


class FleetVehicleTrip(models.Model):
    _inherit = 'fleet.vehicle.trip'

    hr_payslip_id = fields.Many2one('hr.payslip', string="HR Payslip", readonly=True)
    fuel_price_id = fields.Many2one('fleet.fuel.price', string='Fleet Fuel Price', compute='_compute_fuel_price_id', store=True,
                                    help="Technical Field to store matching fuel price during Job Wage computation")
    job_wage_def_id = fields.Many2one('fleet.job.wage.definition', string='Job Wage Definition',
                                    help="Technical Field to store matching Job Wage Definition during Job Wage computation")

    fuel_based_job_wage = fields.Float(string='Fuel Based Job Wage',
                                       compute='_compute_job_wage', store=True,
                                       help="Wage for the driver of the trip which is computed from fuel price and job wage definitions"
                                       " upon confirming this trip")
    job_allowance = fields.Float(string='Job Allowance', compute='_compute_job_wage', store=True,
                                 help="Allowance for the driver of the trip which is computed job wage definitions"
                                 " upon confirming this trip")
    
    @api.depends('fuel_price_id', 'job_wage_def_id')
    def _compute_job_wage(self):
        for r in self:
            if r.fuel_price_id and r.job_wage_def_id:
                r.fuel_based_job_wage = r.job_wage_def_id.consumption * r.fuel_price_id.price_per_liter
                r.job_allowance = r.job_wage_def_id.allowance
            else:
                r.fuel_based_job_wage = 0.0
                r.job_allowance = 0.0
    
    @api.depends('start_date')
    def _compute_fuel_price_id(self):
        for r in self:
            r.fuel_price_id = self.env['fleet.fuel.price'].get_price(r.start_date)
            
    def _get_job_wage(self):
        self.ensure_one()
        fuel_price_id = self.env['fleet.fuel.price'].get_price(self.start_date)
        job_wage_def_id = self.env['fleet.job.wage.definition'].get_consumption(self.route_id, self.vehicle_id)
        return fuel_price_id, job_wage_def_id

    def action_confirm(self):
        super(FleetVehicleTrip, self).action_confirm()
        for r in self:
            fuel_price_id, job_wage_def_id = r._get_job_wage()
            r.write({
                'fuel_price_id': fuel_price_id.id,
                'job_wage_def_id': job_wage_def_id.id,
                })
