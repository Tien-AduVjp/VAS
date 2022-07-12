from odoo import fields, models


class AbstractHrAdvantage(models.AbstractModel):
    _name = 'abstract.hr.advantage'
    _description = 'Hr Advantage Abstract'

    code = fields.Char('Code', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, required=True)
    amount = fields.Monetary(string='Monthly Amount', default=0.0, required=True, help='Monthly Amount for this advantage')
    included_in_payroll_contribution_register = fields.Boolean(string='Included in Payroll Contribution Register')
