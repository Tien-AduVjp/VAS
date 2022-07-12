from odoo import models, fields, api


class employee_advance_reconcile_batch(models.TransientModel):
    _name = 'employee.advance.reconcile.batch'
    _description = 'Employee Advance Reconcile Batch'

    def _default_journal_id(self):
        company_id = self._context.get('company_id', self.env.company.id)
        return self.env['account.journal'].search([('is_advance_journal', '=', True), ('company_id', '=', company_id)], limit=1)

    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    journal_id = fields.Many2one('account.journal', string='Employee Advance Journal', required=True,
                                 default=_default_journal_id, domain=[('is_advance_journal', '=', True)])
    employee_domain_ids = fields.Many2many('hr.employee', string='Employee Domain', compute='_compute_employee_domain_ids',
        relation='employee_domain', column1='employee', column2='reconcile_batch',
        help="The technical field that stores the domain for employee_ids field")
    employee_ids = fields.Many2many('hr.employee', string='Employees')

    @api.depends('journal_id', 'date')
    def _compute_employee_domain_ids(self):
        employee_advances_all = self.env['employee.advance'].search([('state', '=', 'validate')])
        for r in self:
            employee_id_list = []
            employee_advances = employee_advances_all.filtered(lambda e: e.journal_id.id == r.journal_id.id)
            for employee in employee_advances.employee_id:
                if employee._check_employee_unreconciled_advance(r.date, r.journal_id.company_id):
                    employee_id_list.append(employee.id)
            if employee_id_list:
                r.employee_domain_ids = [(6, 0, employee_id_list)]
            else:
                r.employee_domain_ids = False

    def _filter_employee_for_reconcile(self):
        self.ensure_one()
        employee_advances = self.env['employee.advance'].search([('state', '=', 'validate'), ('journal_id', '=', self.journal_id.id)])
        rec_employee_ids = list(set(self.employee_ids.ids).intersection(employee_advances.employee_id.ids))
        employees = self.env['hr.employee']
        rec_employee = employees.browse(rec_employee_ids)

        if rec_employee.exists():
            for emp in rec_employee:
                if emp._check_employee_unreconciled_advance(self.date, self.journal_id.company_id):
                    employees += emp
        return employees

    def action_create(self):
        for r in self:
            for emp in r._filter_employee_for_reconcile():
                self.env['employee.advance.reconcile'].create({
                    'date': r.date,
                    'journal_id': r.journal_id.id,
                    'employee_id': emp.id,
                })
