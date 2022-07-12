from odoo import models, fields, tools
from odoo.addons.to_hr_payroll.models import hr_contract


class PayslipPersonalIncomeTaxAnalysis(models.Model):
    _name = "payslip.personal.income.tax.analysis"
    _description = "Payslip Personal Income Tax Analysis"
    _auto = False
    _rec_name = 'personal_tax_policy'
    _order = 'date asc'

    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    personal_tax_policy = fields.Selection(hr_contract.TAX_POLICY, string='Tax Policy', readonly=True)
    base = fields.Float(string='Tax Computation Base', readonly=True)
    upper_base = fields.Float(string='Taxed Income', readonly=True)
    rate = fields.Float(string='Average Rate (%)', group_operator="sum", required=True, readonly=True)
    tax_amount = fields.Float(string='Tax Amount', readonly=True)
    gross_salary = fields.Float(string='Gross Salary', group_operator="avg", readonly=True)
    personal_tax_rule_id = fields.Many2one('personal.tax.rule', string='Personal Tax Rule', readonly=True)
    slip_id = fields.Many2one('hr.payslip', string='Payslip', readonly=True)
    personal_tax_rule_progress_id = fields.Many2one('personal.tax.rule.progress', string='Tax Escalation', readonly=True)
    date = fields.Datetime('Date', readonly=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    job_id = fields.Many2one('hr.job', string='Job Position', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('verified', 'Verified')], string='Status', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            min(l.id) AS id,
            emp.id AS employee_id,
            l.personal_tax_policy,
            l.base,
            l.upper_base,
            l.tax_amount,
            r.id AS personal_tax_rule_id,
            ps.id AS slip_id,
            ps.gross_salary AS gross_salary,
            (l.tax_amount / ps.gross_salary) * 100 AS rate,
            prog.id AS personal_tax_rule_progress_id,
            ps.date_to AS date,
            c.id AS contract_id,
            CASE WHEN ps.state in ('verify','done')
                THEN 'verified'
                ELSE 'draft'
                END as state,
            dept.id AS department_id,
            j.id AS job_id,
            comp.id AS company_id
        """

        for field in fields.values():
            select_ += field

        from_ = """
                payslip_personal_income_tax l
                    JOIN hr_payslip ps ON (l.slip_id=ps.id)
                    JOIN hr_employee emp ON emp.id = ps.employee_id
                    JOIN personal_tax_rule AS r ON r.id = l.personal_tax_rule_id
                    JOIN hr_contract AS c ON c.id = ps.contract_id
                    JOIN res_company AS comp ON comp.id = ps.company_id
                    LEFT JOIN hr_department AS dept ON dept.id = c.department_id
                    LEFT JOIN hr_job AS j ON j.id = c.job_id
                    LEFT JOIN personal_tax_rule_progress AS prog on (prog.id=l.personal_tax_rule_progress_id)
                %s
        """ % from_clause

        groupby_ = """
            emp.id,
            l.personal_tax_policy,
            l.base,
            l.upper_base,
            l.rate,
            l.tax_amount,
            r.id,
            ps.id,
            ps.gross_salary,
            prog.id,
            ps.date_to,
            c.id,
            dept.id,
            j.id,
            comp.id %s
        """ % (groupby)

        return "%s (SELECT %s FROM %s WHERE ps.state != 'cancel' GROUP BY %s)" % (with_, select_, from_, groupby_)

    def init(self):
        # self._table = payslip_personal_income_tax_analysis
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
