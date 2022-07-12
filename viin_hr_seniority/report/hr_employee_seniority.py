# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import tools
from odoo import fields, models, api, _
from odoo.tools import format_date


class SeniorityReport(models.Model):
    _name = 'hr.employee.seniority'
    _description = "Employee Seniority"
    _auto = False
    _rec_name = 'employee_id'
    _order = 'date_start desc'

    name = fields.Char(string='Contract Reference', readonly=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', readonly=True)
    date_start = fields.Date(string='Start Date', readonly=True)
    date_end = fields.Date(string='End Date', readonly=True)
    is_trial = fields.Boolean(string='Trial', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    job_id = fields.Many2one('hr.job', string='Job Position', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Schedule', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    state = fields.Selection([
        ('draft', 'Incoming'),
        ('open', 'Current'),
        ('close', 'Past'),
        ], string='Status', readonly=True)
    contracts_count = fields.Integer(string='Contracts Count', readonly=True)
    employees_count = fields.Integer(string='Employees Count', readonly=True, group_operator='count_distinct')
    service_years = fields.Float(string='Service Years', readonly=True, compute='_compute_service_years')

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # overrides the default read_group in order to compute the computed fields manually for the group
    
        fields_list = {'service_years'}
    
        # remove all the aggregate functions of non-stored fields to avoid error on pivot view
        def truncate_aggr(field):
            field_no_aggr = field.split(':', 1)[0]
            if field_no_aggr in fields_list:
                return field_no_aggr
            return field
        fields = {truncate_aggr(field) for field in fields}
    
        result = super(SeniorityReport, self).read_group(
            domain,
            list(fields - fields_list),
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy
            )
    
        if any(x in fields for x in fields_list):
            for group_line in result:
    
                # initialise fields to compute to 0 if they are requested
                if 'service_years' in fields:
                    group_line['service_years'] = 0
    
                if group_line.get('__domain'):
                    seniority_lines = self.search(group_line['__domain'])
                else:
                    seniority_lines = self.search([])
                for seniority_line in seniority_lines:
                    if 'service_years' in fields:
                        group_line['service_years'] += seniority_line.service_years
        return result

    def _compute_service_years(self):
        today = fields.Date.today()
        for r in self:
            service_years = 0.0
            if r.date_end and r.date_end <= today:
                date_start = r.date_start
                if not r.is_trial and r.contract_id.trial_date_end and r.contract_id.date_end > r.contract_id.trial_date_end > r.contract_id.date_start:
                    date_start = r.date_start - relativedelta(days=1)
                service_years = self.env['to.base'].get_number_of_years_between_dates(date_start, r.date_end)
            elif r.date_start < today:
                date_start = r.date_start
                if not r.is_trial and r.contract_id.trial_date_end and r.contract_id.trial_date_end > r.contract_id.date_start and \
                        (not r.contract_id.date_end and r.contract_id.trial_date_end < today or r.contract_id.date_end > r.contract_id.trial_date_end):
                    date_start = r.date_start - relativedelta(days=1)
                service_years = self.env['to.base'].get_number_of_years_between_dates(date_start, today)
            r.service_years = service_years

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            row_number() OVER(ORDER BY c1.date_start, c.id) AS id,
            c.id AS contract_id,
            c.name AS name,
            c1.date_start,
            c1.date_end,
            CASE WHEN c1.is_trial=False or c1.is_trial IS NULL THEN False
                ELSE True
                END is_trial,
            emp.id AS employee_id,
            job.id AS job_id,
            dept.id AS department_id,
            cal.id AS resource_calendar_id,
            comp.id AS company_id,
            c.state AS state,
            COUNT(c.id) AS contracts_count,
            COUNT(emp.id) AS employees_count
        """

        for field in fields.values():
            select_ += field

        from_ = """
                hr_contract AS c
                JOIN hr_employee AS emp ON emp.id=c.employee_id
                LEFT JOIN hr_department AS dept ON dept.id = c.department_id
                LEFT JOIN hr_job AS job ON job.id = c.job_id
                JOIN resource_calendar AS cal ON cal.id = c.resource_calendar_id
                JOIN res_company AS comp ON comp.id = c.company_id
                CROSS JOIN UNNEST (
                    array[
                        c.date_start,
                        CASE WHEN c.trial_date_end > c.date_start AND (c.trial_date_end < c.date_end OR (c.date_end IS NULL AND c.trial_date_end < CURRENT_DATE)) THEN (c.trial_date_end + interval '1' day)::date
                            ELSE c.date_end
                            END
                    ],
                      array[
                        CASE WHEN c.trial_date_end > c.date_start AND (c.trial_date_end < c.date_end OR c.date_end IS NULL) THEN c.trial_date_end
                            ELSE c.date_end
                            END,
                        c.date_end
                    ],
                    array[
                        CASE WHEN c.trial_date_end IS NOT NULL AND c.trial_date_end > c.date_start THEN True
                            ELSE False
                            END
                    ]
                ) c1 (date_start, date_end, is_trial)
                %s
        """ % from_clause

        groupby_ = """
            c.name,
            c.id,
            c1.date_start,
            c1.date_end,
            c.state,
            emp.id,
            job.id,
            dept.id,
            cal.id,
            c1.is_trial,
            comp.id %s
        """ % (groupby)

        return """%s (
            SELECT %s
            FROM %s
            WHERE c.state != 'cancel' AND c1.date_start IS NOT NULL and (c1.date_start <> c1.date_end or c1.date_end IS NULL)
            GROUP BY %s
            )""" % (with_, select_, from_, groupby_)

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

    def name_get(self):
        result = []
        for r in self:
            if not r.date_end:
                result.append((r.id, _('%s from %s') % (r.employee_id.name, format_date(r.env, r.date_start))))
            else:
                result.append((r.id, _('%s from %s to %s') % (r.employee_id.name, format_date(r.env, r.date_start), format_date(r.env, r.date_end))))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                '|', '|', '|',
                ('employee_id.job_title', operator, name),
                ('employee_id.name', operator, name),
                ('job_id.name', operator, name),
                ('name', operator, name)
                ]
        records = self.search(domain + args, limit=limit)
        return records.name_get()

    def _prepare_valid_employee_seniority_domain(self):
        return [('state', 'in', ['open', 'close'])]

    def _filter_valid_employee_seniority(self):
        return self.filtered_domain(self._prepare_valid_employee_seniority_domain())
