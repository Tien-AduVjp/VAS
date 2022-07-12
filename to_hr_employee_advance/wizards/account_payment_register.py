from odoo import models, fields


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    # TODO: remove from 15.0
    is_advance_payment = fields.Boolean(string='Employee Advance Payment?', compute='_compute_is_advance_payment')
    employee_id = fields.Many2one('hr.employee', string='Employee')
