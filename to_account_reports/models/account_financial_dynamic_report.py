# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountFinancialDynamicReport(models.Model):
    _name = "account.financial.dynamic.report"
    _description = "Account Report"
    _inherit = "account.report"

    name = fields.Char(translate=True)
    debit_credit = fields.Boolean('Show Credit and Debit Columns')
    line_ids = fields.One2many('account.financial.dynamic.report.line', 'financial_report_id', string='Lines')
    date_range = fields.Boolean('Based on date ranges', default=True, help='specify if the report use date_range or single date')
    comparison = fields.Boolean('Allow comparison', default=True, help='display the comparison filter')
    cash_basis = fields.Boolean('Use cash basis', help='if true, report will always use cash basis, if false, user can choose from filter inside the report')
    analytic = fields.Boolean('Allow analytic filter', help='display the analytic filter')
    hierarchy_option = fields.Boolean('Enable the hierarchy option', help='Display the hierarchy choice in the report options')
    show_journal_filter = fields.Boolean('Allow filtering by journals', help='display the journal filter in the report')
    unfold_all_filter = fields.Boolean('Show unfold all filter', help='display the unfold all options in report')
    company_id = fields.Many2one('res.company', string='Company')
    generated_menu_id = fields.Many2one(
        string='Menu Item', comodel_name='ir.ui.menu', copy=False,
        help="The menu item generated for this report, or None if there isn't any."
    )
    parent_id = fields.Many2one('ir.ui.menu', related="generated_menu_id.parent_id")
    tax_report = fields.Boolean('Tax Report', help="Set to True to automatically filter out journal items that have the boolean field 'tax_exigible' set to False")
    template_ref = fields.Char(string='Reference', translate=True)
    show_report_code = fields.Boolean(string='Show Report Code', help="If set, another column will be displayed on the report to show the code for"
                                      " each and every report line, if a code is specified.")
    show_report_note = fields.Boolean(string='Show Report Note', help="If set, another column will be displayed on the report to show the note for"
                                      " each and every report line.")

    @api.model
    def get_options(self, previous_options=None):
        if self.date_range:
            self.filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}
            if self.comparison:
                self.filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
        else:
            self.filter_date = {'date': '', 'filter': 'today'}
            if self.comparison:
                self.filter_comparison = {'date': '', 'filter': 'no_comparison', 'number_period': 1}
        self.filter_cash_basis = False
        if self.cash_basis:
            self.filter_cash_basis = None
        if self.unfold_all_filter:
            self.filter_unfold_all = False
        if self.show_journal_filter:
            self.filter_journals = True
        self.filter_all_entries = False
        self.filter_analytic = True if self.analytic else None
        self.filter_hierarchy = True if self.hierarchy_option else None
        return super(AccountFinancialDynamicReport, self).get_options(previous_options)
    
    def get_columns_name(self, options):
        columns = [{'name': _('Line Items'), 'class': 'text-center line-item'}]
        if self.show_report_code:
            columns += [{'name':_('Code'), 'class': 'text-center'}]
        if self.show_report_note:
            columns += [{'name':_('Note'), 'class': 'text-center'}]
        if self.debit_credit and not options.get('comparison', {}).get('periods', False):
            columns += [{'name': _('Debit'), 'class': 'number text-center'}, {'name': _('Credit'), 'class': 'number text-center'}]
        dt_to = options['date'].get('date_to') or options['date'].get('date')
        columns += [{'name': self.format_date(dt_to, options['date'].get('date_from', False), options), 'class': 'text-center'}]
        if options.get('comparison') and options['comparison'].get('periods'):
            for period in options['comparison']['periods']:
                columns += [{'name': period.get('string'), 'class': 'text-center'}]
            if options['comparison'].get('number_period') == 1:
                columns += [{'name': '%', 'class': 'text-center'}]
        return columns

    def create_action_and_menu(self, parent_id):
        module = self._context.get('install_module', 'to_account_reports')
        IMD = self.env['ir.model.data']
        for report in self:
            if not report.generated_menu_id:
                action_vals = {
                    'name': report.get_report_name(),
                    'tag': 'af_report_generic',
                    'context': {
                        'model': 'account.financial.dynamic.report',
                        'id': report.id,
                    },
                }
                action_xmlid = "%s.%s" % (module, 'account_financial_dynamic_report_action_' + str(report.id))
                data = dict(xml_id=action_xmlid, values=action_vals, noupdate=True)
                action = self.env['ir.actions.client'].sudo()._load_records([data])

                menu_vals = {
                    'name': report.get_report_name(),
                    'parent_id': parent_id or IMD.xmlid_to_res_id('account.menu_finance_reports'),
                    'action': 'ir.actions.client,%s' % (action.id,),
                }
                menu_xmlid = "%s.%s" % (module, 'account_financial_html_report_menu_' + str(report.id))
                data = dict(xml_id=menu_xmlid, values=menu_vals, noupdate=True)
                menu = self.env['ir.ui.menu'].sudo()._load_records([data])

                self.write({'generated_menu_id': menu.id})

    @api.model
    def create(self, vals):
        parent_id = vals.pop('parent_id', False)
        res = super(AccountFinancialDynamicReport, self).create(vals)
        res.create_action_and_menu(parent_id)
        return res

    def write(self, vals):
        parent_id = vals.pop('parent_id', False)
        res = super(AccountFinancialDynamicReport, self).write(vals)
        if parent_id:
            # this keeps external ids "alive" when upgrading the module
            for report in self:
                report.create_action_and_menu(parent_id)
        return res

    def unlink(self):
        for report in self:
            default_parent_id = self.env['ir.model.data'].xmlid_to_res_id('account.menu_finance_reports')
            menu = self.env['ir.ui.menu'].search([('parent_id', '=', default_parent_id), ('name', '=', report.name)])
            if menu:
                menu.action.unlink()
                menu.unlink()
        return super(AccountFinancialDynamicReport, self).unlink()
    
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        default.update({'name': self._get_copied_name()})
        copied_report_id = super(AccountFinancialDynamicReport, self).copy(default=default)
        for line in self.line_ids:
            line.copy_hierarchy(report_id=self, copied_report_id=copied_report_id)
        return copied_report_id

    def _get_currency_table(self):
        company_ids = self._context.get('company_ids', False)
        filter_company = self.env['res.company']
        if company_ids:
            filter_company = self.env['res.company'].search([('id', '=', company_ids[0])])
        used_currency = filter_company and filter_company.currency_id or self.env.company.currency_id
        currency_table = {}
        for company in self.env['res.company'].search([]):
            if company.currency_id != used_currency:
                currency_table[company.currency_id.id] = used_currency.rate / company.currency_id.rate
        return currency_table

    def get_lines(self, options, line_id=None):
        line_obj = self.line_ids
        if line_id:
            line_obj = self.env['account.financial.dynamic.report.line'].search([('id', '=', line_id)])
        if options.get('comparison') and options.get('comparison').get('periods'):
            line_obj = line_obj.with_context(periods=options['comparison']['periods'])
        currency_table = self._get_currency_table()
        linesDicts = [{} for _ in range(0, len((options.get('comparison') or {}).get('periods') or []) + 2)]
        res = line_obj.with_context(
            cash_basis=options.get('cash_basis') or self.cash_basis,
        ).get_lines(self, currency_table, options, linesDicts)
        return res

    def get_report_name(self):
        return self.name

    def _get_copied_name(self):
        self.ensure_one()
        name = self.name + ' ' + _('(copy)')
        while self.search_count([('name', '=', name)]) > 0:
            name += ' ' + _('(copy)')
        return name
