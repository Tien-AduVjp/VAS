from odoo import models, fields, api


class employee_advance_reconcile_batch(models.TransientModel):
    _name = 'employee.advance.reconcile.batch'
    _description = "Employee Advance Reconcile Batch"

    date = fields.Date(string="Date", required=True, default=fields.Date.today)
    journal_id = fields.Many2one('account.journal', string="Employee Advance Journal", required=True, domain=[('is_advance_journal', '=', True)])
    employee_ids = fields.Many2many('hr.employee', string="Employees")

    @api.onchange('journal_id', 'date')
    def _onchange_journal_id_and_date(self):
        r = {}
        employee_advance = self.env['employee.advance'].search([('state', '=', 'spent'), ('journal_id', '=', self.journal_id.id)])
        employee_ids = []
        if employee_advance:
            for item in employee_advance:
                if item.employee_id.id not in employee_ids:
                    res = self.env['employee.advance.reconcile'].generate_lines(self.journal_id, item.employee_id, self.date)
                    if res['line_dbs']:
                        employee_ids.append(item.employee_id.id)
        if employee_ids:
            self.employee_ids = [(6, 0, employee_ids)]
            r['domain'] = {'employee_ids': [('id', 'in', employee_ids)]}
        else:
            self.employee_ids = False
            r['domain'] = {'employee_ids': [('id', '=', False)]}
        return r

    def action_create(self):
        for r in self:
            for employee in r.employee_ids:
                res = self.env['employee.advance.reconcile'].generate_lines(r.journal_id, employee, r.date)
                if not res['line_dbs']:
                    continue
                self.env['employee.advance.reconcile'].create({
                    'date': r.date,
                    'journal_id': r.journal_id.id,
                    'employee_id': employee.id,
                    'line_db_ids': res['line_dbs'],
                    'line_cr_ids': res['line_crs'],
                })
