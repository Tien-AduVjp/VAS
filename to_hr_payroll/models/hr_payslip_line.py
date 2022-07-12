from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipLine(models.Model):
    _name = 'hr.payslip.line'
    _inherit = 'abstract.hr.salary.rule'
    _description = 'Payslip Line'
    _order = 'contract_id, sequence'

    slip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade')
    payslip_run_id = fields.Many2one(related='slip_id.payslip_run_id', store=True, index=True)
    currency_id = fields.Many2one(related='slip_id.currency_id')
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Rule', required=True)
    struct_id = fields.Many2one(related='salary_rule_id.struct_id')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True, index=True)
    rate = fields.Float(string='Rate (%)', digits='Payroll Rate', default=100.0)
    amount = fields.Monetary()
    quantity = fields.Float(digits='Payroll', default=1.0)
    total = fields.Monetary(compute='_compute_total', string='Total', store=True)
    date_from = fields.Date(string='Date From', related='slip_id.date_from', store=True)
    date_to = fields.Date(string='Date To', related='slip_id.date_to', store=True)

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            line.total = float(line.quantity) * line.amount * line.rate / 100

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'employee_id' not in values or 'contract_id' not in values:
                payslip = self.env['hr.payslip'].browse(values.get('slip_id'))
                values['employee_id'] = values.get('employee_id') or payslip.employee_id.id
                values['contract_id'] = values.get('contract_id') or payslip.contract_id and payslip.contract_id.id
                if not values['contract_id']:
                    raise UserError(_('You must set a contract to create a payslip line.'))
        return super(HrPayslipLine, self).create(vals_list)

