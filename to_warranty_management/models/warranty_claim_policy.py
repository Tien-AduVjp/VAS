from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import UserError

class WarrantyClaimPolicy(models.Model):
    _name = 'warranty.claim.policy'
    _description = "Warranty Claim Policy"

    product_milestone_id = fields.Many2one('product.milestone', string='Milestone', required=True)
    state = fields.Selection([('undefine', 'Undefined'),
                              ('ok', 'OK'),
                              ('not_ok', 'Not OK')], string='State', default='undefine', compute='_compute_state', readonly=True)
    warranty_claim_id = fields.Many2one('warranty.claim', string='Warranty Claim')
    current_measurement = fields.Float(string='Current Measurement')
    apply_to = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase')], string='Apply to', required=True)
    operation_start = fields.Float(string='Operation Start')
    operation_end = fields.Float(string='Operation End', compute='_compute_warranty_end', store=True)

    _sql_constraints = [
        ('policy_unique',
         'unique(product_milestone_id,warranty_claim_id,apply_to)',
         "Policy must be unique!"),
    ]

    @api.constrains('operation_start', 'current_measurement')
    def _check_warranty_milestone_indicator(self):
        for r in self:
            if r.current_measurement < r.operation_start:
                raise UserError(_("The Current Measurement cannot be less than the Operation Start."))

    @api.depends('operation_start', 'product_milestone_id')
    def _compute_warranty_end(self):
        for r in self:
            operation_start = r.operation_start or 0.0
            amount = r.product_milestone_id and r.product_milestone_id.amount or 0
            r.operation_end = operation_start + amount

    @api.depends('product_milestone_id', 'operation_end', 'current_measurement')
    def _compute_state(self):
        for r in self:
            rounding = r.product_milestone_id.uom_id.rounding
            if rounding:
                compare_result = float_compare(r.operation_end, r.current_measurement, precision_rounding = rounding)
            else:
                compare_result = float_compare(r.operation_end, r.current_measurement, precision_digits = 2)
            if compare_result >= 0:
                r.state = 'ok'
            else:
                r.state = 'not_ok'

    def _prepare_warranty_claim_policy_on_lot_data(self):
        return {
            'product_milestone_id': self.product_milestone_id.id,
            'apply_to': self.apply_to,
            'operation_start': self.operation_start,
            'current_measurement': self.current_measurement
            }
