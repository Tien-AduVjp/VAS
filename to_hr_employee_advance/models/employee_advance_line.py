from odoo import fields, models


class HrEmployeeAdvanceLine(models.Model):
    _name = 'employee.advance.line'
    _description = 'HR Employee Advance Line'

    advance_id = fields.Many2one('employee.advance', string="Employee Advance", ondelete='cascade', index=True)
    name = fields.Char(string="Description", required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='advance_id.currency_id')
    amount = fields.Monetary(string="Amount", required=True)
