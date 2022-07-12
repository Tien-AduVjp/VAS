# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
import copy
import json
import io
import logging
import lxml.html

from odoo.tools.misc import xlsxwriter

from odoo import models, api, fields, _
from datetime import timedelta, datetime, date
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from babel.dates import get_quarter_names
from odoo.tools.misc import formatLang, format_date
from odoo.tools import config
from odoo.addons.web.controllers.main import clean_action
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AccountReport(models.AbstractModel):
    _name = 'account.report'
    _description = 'Accounting Report'

    filter_date = None
    filter_cash_basis = None
    filter_all_entries = None
    filter_comparison = None
    filter_journals = None
    filter_analytic = None
    filter_unfold_all = None
    filter_hierarchy = None
    
    show_parent_line_first = fields.Boolean(string='Show Parent Lines First', default=False,
                                            help="If set, the parent lines should be displayed before the child lines on reports.")

    def _build_options(self, previous_options=None):
        if not previous_options:
            previous_options = {}
        options = {}
        filter_list = [attr for attr in dir(self) if attr.startswith('filter_') and len(attr) > 7 and not callable(getattr(self, attr))]
        for element in filter_list:
            filter_name = element[7:]
            options[filter_name] = getattr(self, element)

        group_multi_company = self.env['ir.model.data'].xmlid_to_object('base.group_multi_company')
        if self.env.user.id in group_multi_company.users.ids:
            # We have a user with multi-company
            options['multi_company'] = [{'id': c.id, 'name': c.name, 'selected': True if c.id in self.env.context.get('allowed_company_ids',[]) else False} for c in self.env.user.company_ids]
        if options.get('journals'):
            options['journals'] = self.get_journals()

        options['unfolded_lines'] = []
        # Merge old options with default from this report
        for key, value in options.items():
            if key in previous_options and value is not None and previous_options[key] is not None:
                # special case handler for date and comparison as from one report to another, they can have either a date range or single date
                if key == 'date' or key == 'comparison':
                    if key == 'comparison':
                        options[key]['number_period'] = previous_options[key]['number_period']
                    options[key]['filter'] = 'custom'
                    if previous_options[key].get('filter', 'custom') != 'custom':
                        # just copy filter and let the system compute the correct date from it
                        options[key]['filter'] = previous_options[key]['filter']
                    elif value.get('date_from') is not None and not previous_options[key].get('date_from'):
                        company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(datetime.strptime(previous_options[key]['date'], DF))
                        options[key]['date_from'] = company_fiscalyear_dates['date_from'].strftime(DF)
                        options[key]['date_to'] = previous_options[key]['date']
                    elif value.get('date') is not None and not previous_options[key].get('date'):
                        options[key]['date'] = previous_options[key]['date_to']
                    else:
                        options[key] = previous_options[key]
                elif key == 'multi_company':
                    for previous_company in previous_options[key]:
                        for company in options[key]:
                            if company['id'] == previous_company['id'] and company['selected'] != previous_company['selected']:
                                options[key] = previous_options[key]
                                break
                else:
                    options[key] = previous_options[key]
        return options

    @api.model
    def get_options(self, previous_options=None):
        # Be sure that user has group analytic if a report tries to display analytic
        if self.filter_analytic:
            self.filter_analytic = self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids and True or None
            self.filter_analytic_tags = [] if self.filter_analytic else None
            self.filter_analytic_accounts = [] if self.filter_analytic else None

        return self._build_options(previous_options)

    # TO BE OVERWRITTEN
    def get_columns_name(self, options):
        return []

    # TO BE OVERWRITTEN
    def get_lines(self, options, line_id=None):
        return []

    # TO BE OVERWRITTEN
    def get_templates(self):
        return {
                'main_template': 'to_account_reports.main_template',
                'line_template': 'to_account_reports.line_template',
                'footnotes_template': 'to_account_reports.footnotes_template',
                'search_template': 'to_account_reports.search_template',
                'print_template': 'to_account_reports.print_template',
                'header_layout': 'web.internal_layout',
                'render_print_template': 'to_account_reports.main_template'
        }

    # TO BE OVERWRITTEN
    def get_report_name(self):
        return _('General Report')

    def get_report_filename(self, options):
        """The name that will be used for the file when downloading pdf,xlsx,..."""
        return self.get_report_name().lower().replace(' ', '_')

    def execute_action(self, options, params=None):
        action_id = int(params.get('actionId'))
        action = self.env['ir.actions.actions'].browse([action_id])
        action_type = action.type
        action = self.env[action.type].browse([action_id])
        action_read = action.read()[0]
        if action_type == 'ir.actions.client':
            # Check if we are opening another report and if yes, pass options and ignore_session
            if action.tag == 'af_report_generic':
                options['unfolded_lines'] = []
                options['unfold_all'] = False
                another_report_context = safe_eval(action_read['context'])
                another_report = self.browse(another_report_context['id'])
                if not self.date_range and another_report.date_range:
                    # Don't propagate the filter if current report is date based while the targetted
                    # report is date_range based, because the semantic is not the same:
                    # 'End of Following Month' in BS != 'Last Month' in P&L (it has to go from 1st day of fiscalyear)
                    options['date'].pop('filter')
                action_read.update({'options': options, 'ignore_session': 'read'})
        if params.get('id'):
            # Add the id of the account.financial.dynamic.report.line in the action's context
            context = action_read.get('context') and safe_eval(action_read['context']) or {}
            context.setdefault('active_id', int(params['id']))
            action_read['context'] = context
        return action_read

    def open_tax(self, options, params=None):
        active_id = int(str(params.get('id')).split('_')[0])
        domain = [('date', '>=', options.get('date').get('date_from')), ('date', '<=', options.get('date').get('date_to')),
                  '|', ('tax_ids', 'in', [active_id]), ('tax_line_id', 'in', [active_id])]
        if not options.get('all_entries'):
            domain.append(('move_id.state', '=', 'posted'))
        action = self.env.ref('account.action_move_line_select_tax_audit').read()[0]
        ctx = self.env.context.copy()
        ctx.update({'active_id': active_id, })
        action = clean_action(action)
        action['domain'] = domain
        action['context'] = ctx
        return action
    
    def open_document(self, options, params=None):
        if not params:
            params = {}
        ctx = self.env.context.copy()
        ctx.pop('id', '')
        aml_id = params.get('id')
        document = params.get('object', 'account.move')
        if aml_id:
            aml = self.env['account.move.line'].browse(aml_id)
            view_name = 'view_move_form'
            res_id = aml.move_id.id
            if document == 'account.move' and aml.move_id.id:
                res_id = aml.move_id.id
                if aml.move_id.type in ('in_refund', 'in_invoice'):
                    view_name = 'view_move_form'
                    ctx['journal_type'] = 'purchase'
                elif aml.move_id.type in ('out_refund', 'out_invoice'):
                    view_name = 'view_move_form'
                    ctx['journal_type'] = 'sale'
                ctx['type'] = aml.move_id.type
                ctx['default_type'] = aml.move_id.type
            elif document == 'account.payment' and aml.payment_id.id:
                view_name = 'view_account_payment_form'
                res_id = aml.payment_id.id
            view_id = self.env['ir.model.data'].get_object_reference('account', view_name)[1]
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': document,
                'view_id': view_id,
                'res_id': res_id,
                'context': ctx,
            }

    def view_too_many(self, options, params=None):
        model, active_id = params.get('actionId').split(',')
        ctx = self.env.context.copy()
        if model == 'account':
            action = self.env.ref('account.action_move_line_select').read()[0]
            ctx.update({
                'search_default_account_id': [int(active_id)],
                'active_id': int(active_id),
                })
        if model == 'partner':
            action = self.env.ref('account.action_move_line_select_by_partner').read()[0]
            ctx.update({
                'search_default_partner_id': [int(active_id)],
                'active_id': int(active_id),
                })
        action = clean_action(action)
        action['context'] = ctx
        return action

    def open_journal_items(self, options, params):
        action = self.env.ref('account.action_move_line_select').read()[0]
        action = clean_action(action)
        ctx = self.env.context.copy()

        if params and 'id' in params:
            active_id = params['id']
            ctx.update({
                    'search_default_account_id': [active_id],
            })
            action['context'] = ctx
        if options:
            domain = expression.normalize_domain(safe_eval(action.get('domain', '[]')))
            if options.get('analytic_accounts'):
                analytic_ids = [int(r) for r in options['analytic_accounts']]
                domain = expression.AND([domain, [('analytic_account_id', 'in', analytic_ids)]])
            if options.get('date'):
                opt_date = options['date']
                if opt_date.get('date_from'):
                    domain = expression.AND([domain, [('date', '>=', opt_date['date_from'])]])
                if opt_date.get('date_to'):
                    domain = expression.AND([domain, [('date', '<=', opt_date['date_to'])]])
            action['domain'] = domain
        return action
    
    def open_general_ledger(self, options, params=None):
        if not params:
            params = {}
        ctx = self.env.context.copy()
        ctx.pop('id', '')
        action = self.env.ref('to_account_reports.action_af_report_general_ledger').read()[0]
        options['unfolded_lines'] = ['account_%s' % (params.get('id', ''),)]
        options['unfold_all'] = False
        ctx.update({'model': 'account.general.ledger'})
        action.update({'options': options, 'context': ctx, 'ignore_session': 'read'})
        return action

    def set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        ctx = self.env.context.copy()
        if options.get('cash_basis'):
            ctx['cash_basis'] = True
        if options.get('date') and options['date'].get('date_from'):
            ctx['date_from'] = options['date']['date_from']
        if options.get('date'):
            ctx['date_to'] = options['date'].get('date_to') or options['date'].get('date')
        if options.get('all_entries') is not None:
            ctx['state'] = options.get('all_entries') and 'all' or 'posted'
        if options.get('journals'):
            ctx['journal_ids'] = [j.get('id') for j in options.get('journals') if j.get('selected')]
        company_ids = []
        if options.get('multi_company'):
            company_ids = [c.get('id') for c in options['multi_company'] if c.get('selected')]
            company_ids = company_ids if len(company_ids) > 0 else [c.get('id') for c in options['multi_company']]
        ctx['company_ids'] = len(company_ids) > 0 and company_ids or [self.env.company.id]
        if options.get('analytic_accounts'):
            ctx['analytic_account_ids'] = self.env['account.analytic.account'].browse([int(acc) for acc in options['analytic_accounts']])
        if options.get('analytic_tags'):
            ctx['analytic_tag_ids'] = self.env['account.analytic.tag'].browse([int(t) for t in options['analytic_tags']])
        return ctx
    
    def reverse(self, values):
        """Utility method used to reverse a list, this method is used during template generation in order to reverse periods for example"""
        if type(values) != list:
            return values
        else:
            inv_values = copy.deepcopy(values)
            inv_values.reverse()
        return inv_values

    def get_rp_informations(self, options):
        options = self.get_options(options)
        # apply date and date_comparison filter
        options = self.apply_date_filter(options)
        options = self.apply_cmp_filter(options)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic_accounts') is not None:
            searchview_dict['analytic_accounts'] = self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids and [(t.id, t.name) for t in self.env['account.analytic.account'].search([])] or False
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
            
        if options.get('analytic_tags') is not None:
            searchview_dict['analytic_tags'] = self.env.user.id in self.env.ref('analytic.group_analytic_tags').users.ids and [(t.id, t.name) for t in self.env['account.analytic.tag'].search([])] or False
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
            
        if options.get('analytic') is not None:
            searchview_dict['analytic_accounts'] = self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids and [(t.id, t.name) for t in self.env['account.analytic.account'].search([])] or False
            searchview_dict['analytic_tags'] = self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids and [(t.id, t.name) for t in self.env['account.analytic.tag'].search([])] or False
        report_manager = self.get_report_manager(options)
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self.get_reports_buttons(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view'].render_template(self.get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        return info

    @api.model
    def create_hierarchy(self, lines):
        # Avoid redundant browsing.
        accounts_cache = {}

        MOST_SORT_PRIO = 0
        LEAST_SORT_PRIO = 99

        # Retrieve account either from cache, either by browsing.
        def get_account(id):
            if id not in accounts_cache:
                accounts_cache[id] = self.env['account.account'].browse(id)
            return accounts_cache[id]

        # Create codes path in the hierarchy based on account.
        def get_account_codes(account):
            # A code is tuple(sort priority, actual code)
            codes = []
            if account.group_id:
                group = account.group_id
                while group:
                    code = '%s %s' % (group.code_prefix or '', group.name)
                    codes.append((MOST_SORT_PRIO, code))
                    group = group.parent_id
            else:
                # Limit to 3 levels.
                code = account.code[:3]
                while code:
                    codes.append((MOST_SORT_PRIO, code))
                    code = code[:-1]
            return list(reversed(codes))

        # Add the report line to the hierarchy recursively.
        def add_line_to_hierarchy(line, codes, level_dict, depth=None):
            if not codes:
                return
            if not depth:
                depth = line.get('level', 1)
            level_dict.setdefault('depth', depth)
            level_dict.setdefault('parent_id', line.get('parent_id'))
            level_dict.setdefault('children', {})
            code = codes[0]
            codes = codes[1:]
            level_dict['children'].setdefault(code, {})

            if codes:
                add_line_to_hierarchy(line, codes, level_dict['children'][code], depth=depth + 1)
            else:
                level_dict['children'][code].setdefault('lines', [])
                level_dict['children'][code]['lines'].append(line)

        # Merge a list of columns together and take care about str values.
        def merge_columns(columns):
            return ['n/a' if any(isinstance(i, str) for i in x) else sum(x) for x in zip(*columns)]

        # Get_lines for the newly computed hierarchy.
        def get_hierarchy_lines(values, depth=1):
            lines = []
            sum_sum_columns = []
            for base_line in values.get('lines', []):
                lines.append(base_line)
                sum_sum_columns.append([c.get('no_format_name', c['name']) for c in base_line['columns']])

            # For the last iteration, there might not be the children key (see add_line_to_hierarchy)
            for key in sorted(values.get('children', {}).keys()):
                sum_columns, sub_lines = get_hierarchy_lines(values['children'][key], depth=values['depth'])
                header_line = {
                    'id': 'hierarchy',
                    'name': key[1],  # second member of the tuple
                    'unfoldable': False,
                    'unfolded': True,
                    'level': values['depth'],
                    'parent_id': values['parent_id'],
                    'columns': [{'name': self.format_value(c) if not isinstance(c, str) else c} for c in sum_columns],
                }
                if key[0] == LEAST_SORT_PRIO:
                    header_line['style'] = 'font-style:italic;'
                lines += [header_line] + sub_lines
                sum_sum_columns.append(sum_columns)
            return merge_columns(sum_sum_columns), lines

        def deep_merge_dict(source, destination):
            for key, value in source.items():
                if isinstance(value, dict):
                    # get node or create one
                    node = destination.setdefault(key, {})
                    deep_merge_dict(value, node)
                else:
                    destination[key] = value

            return destination

        # Hierarchy of codes.
        accounts_hierarchy = {}

        new_lines = []
        no_group_lines = []
        # If no account.group at all, we need to pass once again in the loop to dispatch
        # all the lines across their account prefix, hence the None
        for line in lines + [None]:
            # Only deal with lines grouped by accounts.
            # And discriminating sections defined by account.financial.dynamic.report.line
            is_grouped_by_account = line and line.get('caret_options') == 'account.account'
            if not is_grouped_by_account or not line:

                # No group code found in any lines, compute it automatically.
                no_group_hierarchy = {}
                for no_group_line in no_group_lines:
                    codes = [(LEAST_SORT_PRIO, _('(No Group)'))]
                    if not accounts_hierarchy:
                        account = get_account(no_group_line.get('id'))
                        codes = get_account_codes(account)
                    add_line_to_hierarchy(no_group_line, codes, no_group_hierarchy)
                no_group_lines = []

                deep_merge_dict(no_group_hierarchy, accounts_hierarchy)

                # Merge the newly created hierarchy with existing lines.
                if accounts_hierarchy:
                    new_lines += get_hierarchy_lines(accounts_hierarchy)[1]
                    accounts_hierarchy = {}

                if line:
                    new_lines.append(line)
                continue

            # Exclude lines having no group.
            account = get_account(line.get('id'))
            if not account.group_id:
                no_group_lines.append(line)
                continue

            codes = get_account_codes(account)
            add_line_to_hierarchy(line, codes, accounts_hierarchy)

        return new_lines

    def get_html(self, options, line_id=None, additional_context=None):
        templates = self.get_templates()
        report_manager = self.get_report_manager(options)
        multi_company = options.get('multi_company', False)
        company_ids = []
        if multi_company:
            for company in multi_company:
                company_id = company.get('id', 0)
                if company.get('selected', False) and company_id:
                    company_ids.append(company_id)
        filter_company = self.env['res.company']
        if company_ids:
            filter_company = self.env['res.company'].search([('id', '=', company_ids[0])])
        report = {'name': self.get_report_name(),
                'summary': report_manager.summary,
                'company_name': filter_company and filter_company.name or self.env.company.name,
                'company_currency': filter_company and filter_company.currency_id.name or self.env.company.currency_id.name}
        lines = self.with_context(self.set_context(options)).get_lines(options, line_id=line_id)

        if options.get('hierarchy'):
            lines = self.create_hierarchy(lines)

        footnotes_to_render = []
        if self.env.context.get('print_mode', False):
            # we are in print mode, so compute footnote number and include them in lines values, otherwise, let the js compute the number correctly as
            # we don't know all the visible lines.
            footnotes = dict([(str(f.line), f) for f in report_manager.footnotes_ids])
            number = 0
            for line in lines:
                f = footnotes.get(str(line.get('id')))
                if f:
                    number += 1
                    line['footnote'] = str(number)
                    footnotes_to_render.append({'id': f.id, 'number': number, 'text': f.text})

        rcontext = {'report': report,
                    'lines': {'columns_header': self.get_columns_name(options), 'lines': lines},
                    'options': options,
                    'context': self.env.context,
                    'model': self,
                }
        if additional_context and type(additional_context) == dict:
            rcontext.update(additional_context)
        render_template = templates.get('main_template', 'to_account_reports.main_template')
        if line_id is not None:
            render_template = templates.get('line_template', 'to_account_reports.line_template')
        if self.env.context.get('print_mode', False):
            render_template = templates.get('render_print_template', 'to_account_reports.main_template')
        html = self.env['ir.ui.view'].render_template(
            render_template,
            values=dict(rcontext),
        )
        if self.env.context.get('print_mode', False):
            for k, v in self.replace_class().items():
                html = html.replace(k, v)
            # append footnote as well
            html = html.replace(b'<div class="js_af_report_footnotes"></div>', self.get_html_footnotes(footnotes_to_render))
        return html

    def get_html_footnotes(self, footnotes):
        template = self.get_templates().get('footnotes_template', 'to_account_reports.footnotes_template')
        rcontext = {'footnotes': footnotes, 'context': self.env.context}
        html = self.env['ir.ui.view'].render_template(template, values=dict(rcontext))
        return html

    def get_report_manager(self, options):
        domain = [('report_name', '=', self._name)]
        domain = (domain + [('financial_report_id', '=', self.id)]) if 'id' in dir(self) else domain
        selected_companies = []
        if options.get('multi_company'):
            selected_companies = [c['id'] for c in options['multi_company'] if c.get('selected')]
        if len(selected_companies) == 1:
            domain += [('company_id', '=', selected_companies[0])]
        existing_manager = self.env['account.report.manager'].search(domain, limit=1)
        if not existing_manager:
            existing_manager = self.env['account.report.manager'].create({'report_name': self._name, 'company_id': selected_companies and selected_companies[0] or False, 'financial_report_id': self.id if 'id' in dir(self) else False})
        return existing_manager
    
    def get_reports_buttons(self):
        return [{'name': _('Print PDF'), 'action': 'print_pdf'}, {'name': _('Print XLSX'), 'action': 'print_xlsx'}]

    def _get_filter_journals(self):
        return self.env['account.journal'].search([('company_id', 'in', self.env.user.company_ids.ids or [self.env.company.id])], order="company_id, name")

    def get_journals(self):
        journals_read = self._get_filter_journals()
        journals = []
        previous_company = False
        for c in journals_read:
            if c.company_id != previous_company:
                journals.append({'id': 'divider', 'name': c.company_id.name})
                previous_company = c.company_id
            journals.append({'id': c.id, 'name': c.name, 'code': c.code, 'type': c.type, 'selected': False})
        return journals

    def format_date(self, dt_to, dt_from, options, dt_filter='date'):
        # previously get_full_date_names
        options_filter = options[dt_filter].get('filter', '')
        if isinstance(dt_to, (str,)):
            dt_to = datetime.strptime(dt_to, DF)
        if dt_from and isinstance(dt_from, (str,)):
            dt_from = datetime.strptime(dt_from, DF)
        if 'month' in options_filter:
            return format_date(self.env, dt_to.strftime(DF), date_format='MMM YYYY')
        if 'quarter' in options_filter:
            quarter = (dt_to.month - 1) // 3 + 1
            return (u'%s\N{NO-BREAK SPACE}%s') % (get_quarter_names('abbreviated', locale=self._context.get('lang') or 'en_US')[quarter], dt_to.year)
        if 'year' in options_filter:
            if self.env.company.fiscalyear_last_day == 31 and int(self.env.company.fiscalyear_last_month) == 12:
                return dt_to.strftime('%Y')
            else:
                return '%s - %s' % ((dt_to.year - 1), dt_to.year)
        if not dt_from:
            return _('As of %s') % (format_date(self.env, dt_to.strftime(DF)),)
        return _('From %s <br/> to  %s').replace('<br/>', '\n') % (format_date(self.env, dt_from.strftime(DF)), format_date(self.env, dt_to.strftime(DF)))
    
    def format_value(self, value, currency=False):
        if self.env.context.get('no_format'):
            return value
        company_ids = self._context.get('company_ids', False)
        filter_company = self.env['res.company']
        if company_ids:
            filter_company = self.env['res.company'].search([('id', '=', company_ids[0])])
        if currency:
            currency_id = currency
        else:
            currency_id = filter_company and filter_company.currency_id or self.env.company.currency_id
        if currency_id.is_zero(value):
            # don't print -0.0 in reports
            value = abs(value)
        res = formatLang(self.env, value, currency_obj=currency_id)
        return res

    def apply_cmp_filter(self, options):
        if not options.get('comparison'):
            return options
        options['comparison']['periods'] = []
        cmp_filter = options['comparison'].get('filter')
        if not cmp_filter:
            return options
        if cmp_filter == 'no_comparison':
            if options['comparison'].get('date_from') != None:
                options['comparison']['date_from'] = ""
                options['comparison']['date_to'] = ""
            else:
                options['comparison']['date'] = ""
            options['comparison']['string'] = _('No comparison')
            return options
        elif cmp_filter == 'custom':
            date_from = options['comparison'].get('date_from')
            date_to = options['comparison'].get('date_to') or options['comparison'].get('date')
            display_value = self.format_date(date_to, date_from, options, dt_filter='comparison')
            if date_from:
                vals = {'date_from': date_from, 'date_to': date_to, 'string': display_value}
            else:
                vals = {'date': date_to, 'string': display_value}
            options['comparison']['periods'] = [vals]
            return options
        else:
            dt_from = False
            options_filter = options['date'].get('filter', '')
            if options['date'].get('date_from'):
                dt_from = datetime.strptime(options['date'].get('date_from'), "%Y-%m-%d")
            dt_to = options['date'].get('date_to') or options['date'].get('date')
            dt_to = datetime.strptime(dt_to, "%Y-%m-%d")
            display_value = False
            number_period = options['comparison'].get('number_period', 1) or 0
            for index in range(0, number_period):
                if cmp_filter == 'same_last_year' or options_filter in ('this_year', 'last_year'):
                    if dt_from:
                        dt_from = dt_from + relativedelta(years=-1)
                    dt_to = dt_to + relativedelta(years=-1)
                elif cmp_filter == 'previous_period':
                    if options_filter in ('this_month', 'last_month', 'today'):
                        dt_from = dt_from and (dt_from - timedelta(days=1)).replace(day=1) or dt_from
                        dt_to = dt_to.replace(day=1) - timedelta(days=1)
                    elif options_filter in ('this_quarter', 'last_quarter'):
                        dt_to = dt_to.replace(month=(dt_to.month + 10) % 12, day=1) - timedelta(days=1)
                        dt_from = dt_from and dt_from.replace(month=dt_to.month - 2, year=dt_to.year) or dt_from
                    elif options_filter == 'custom':
                        if not dt_from:
                            dt_to = dt_to.replace(day=1) - timedelta(days=1)
                        else:
                            previous_dt_to = dt_to
                            dt_to = dt_from - timedelta(days=1)
                            dt_from = dt_from - timedelta(days=(previous_dt_to - dt_from).days + 1)
                display_value = self.format_date(dt_to, dt_from, options)

                if dt_from:
                    vals = {'date_from': dt_from.strftime(DF), 'date_to': dt_to.strftime(DF), 'string': display_value}
                else:
                    vals = {'date': dt_to.strftime(DF), 'string': display_value}
                options['comparison']['periods'].append(vals)
        if len(options['comparison'].get('periods', [])) > 0:
            for k, v in options['comparison']['periods'][0].items():
                if k in ('date', 'date_from', 'date_to', 'string'):
                    options['comparison'][k] = v
        return options
    
    def apply_date_filter(self, options):
        if not options.get('date'):
            return options
        options_filter = options['date'].get('filter')
        if not options_filter:
            return options
        today = fields.Date.today()
        dt_from = options['date'].get('date_from') is not None and today or False
        if options_filter == 'custom':
            dt_from = options['date'].get('date_from', False)
            dt_to = options['date'].get('date_to', False) or options['date'].get('date', False)
            if not dt_to:
                dt_to = today
                options['date']['date_to'] = today
            options['date']['string'] = self.format_date(dt_to, dt_from, options)
            return options
        if options_filter == 'today':
            company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fields.Datetime.now())
            dt_from = dt_from and company_fiscalyear_dates['date_from'] or False
            dt_to = today
        elif options_filter == 'this_month':
            dt_from = dt_from and today.replace(day=1) or False
            dt_to = (today.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        elif options_filter == 'this_quarter':
            quarter = (today.month - 1) // 3 + 1
            dt_to = (today.replace(month=quarter * 3, day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            dt_from = dt_from and dt_to.replace(day=1, month=dt_to.month - 2, year=dt_to.year) or False
        elif options_filter == 'this_year':
            company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fields.Datetime.now())
            dt_from = dt_from and company_fiscalyear_dates['date_from'] or False
            dt_to = company_fiscalyear_dates['date_to']
        elif options_filter == 'last_month':
            dt_to = today.replace(day=1) - timedelta(days=1)
            dt_from = dt_from and dt_to.replace(day=1) or False
        elif options_filter == 'last_quarter':
            quarter = (today.month - 1) // 3 + 1
            quarter = quarter - 1 if quarter > 1 else 4
            dt_to = (today.replace(month=quarter * 3, day=1, year=today.year if quarter != 4 else today.year - 1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            dt_from = dt_from and dt_to.replace(day=1, month=dt_to.month - 2, year=dt_to.year) or False
        elif options_filter == 'last_year':
            company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fields.Datetime.now().replace(year=today.year - 1))
            dt_from = dt_from and company_fiscalyear_dates['date_from'] or False
            dt_to = company_fiscalyear_dates['date_to']
        if dt_from:
            options['date']['date_from'] = dt_from.strftime(DF)
            options['date']['date_to'] = dt_to.strftime(DF)
        else:
            options['date']['date'] = dt_to.strftime(DF)
        options['date']['string'] = self.format_date(dt_to, dt_from, options)
        return options

    def print_pdf(self, options):
        return {
                'type': 'ir_actions_af_report_dl',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'pdf',
                         'financial_id': self.env.context.get('id'),
                         }
                }

    def get_pdf(self, options, minimal_layout=True):
        if not config['test_enable']:
            self = self.with_context(commit_assetsbundle=True)

        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.company,
            'template_ref': self.get_template_ref()
        }

        body = self.env['ir.ui.view'].render_template(
            self.get_templates().get('print_template', 'to_account_reports.print_template'),
            values=dict(rcontext),
        )
        body_html = self.with_context(print_mode=True).get_html(options)

        body = body.replace(b'<body class="o_af_reports_body_print">', b'<body class="o_af_reports_body_print">' + body_html)
        if minimal_layout:
            header = self.env['ir.actions.report'].render_template(self.get_templates().get('header_layout', 'web.internal_layout'), values=rcontext)
            footer = ''
            if self.get_templates().get('footer_layout', False):
                footer = self.env['ir.actions.report'].render_template(self.get_templates().get('footer_layout'), values=rcontext)
                footer = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=footer))
            spec_paperformat_args = {'data-report-margin-top': 40, 'data-report-header-spacing': 35}
            header = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=header))
        else:
            rcontext.update({
                    'css': '',
                    'o': self.env.user,
                    'res_company': self.env.company,
                })
            header = self.env['ir.actions.report'].render_template("web.external_layout", values=rcontext)
            header = header.decode('utf-8')  # Ensure that headers and footer are correctly encoded
            spec_paperformat_args = {}
            # parse header as new header contains header, body and footer
            try:
                root = lxml.html.fromstring(header)
                match_klass = "//div[contains(concat(' ', normalize-space(@class), ' '), ' {} ')]"

                for node in root.xpath(match_klass.format('header')):
                    headers = lxml.html.tostring(node)
                    headers = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=headers))

                for node in root.xpath(match_klass.format('footer')):
                    footer = lxml.html.tostring(node)
                    footer = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=footer))

            except lxml.etree.XMLSyntaxError:
                headers = header
                footer = ''
            header = headers

        landscape = False
        if len(self.with_context(print_mode=True).get_columns_name(options)) > 5:
            landscape = True

        return self.env['ir.actions.report']._run_wkhtmltopdf(
            [body],
            header=header, footer=footer,
            landscape=landscape,
            specific_paperformat_args=spec_paperformat_args
        )

    def print_xml(self, options):
        return {
                'type': 'ir_actions_af_report_dl',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'xml',
                         'financial_id': self.env.context.get('id'),
                         }
                }

    def get_xml(self, options):
        return False
    
    def print_xlsx(self, options):
        return {
                'type': 'ir_actions_af_report_dl',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'xlsx',
                         'financial_id': self.env.context.get('id'),
                         }
                }

    def get_xlsx(self, options, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self.get_report_name()[:31])
        sheet.set_default_row(20)

        report_code_style = workbook.add_format({'font_name': 'Arial', 'align': 'center', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1})
        
        def_style = workbook.add_format({'font_name': 'Arial', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'align': 'center', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1})
        super_col_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'align': 'center', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1})
        level_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'top': 1, 'bottom': 1, 'left': 1, 'right': 1})
        level_1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'top': 1, 'bottom': 1, 'left': 1, 'right': 1})
        level_2_style = workbook.add_format({'font_name': 'Arial', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1})
        level_3_style = def_style

        start_row = 0  # row start of the table
        super_columns = self._get_super_columns(options)
        x_merge = super_columns.get('merge') or 1
        x_offset = super_columns.get('x_offset', 0)
        y_offset = bool(super_columns.get('columns')) and (start_row + 1) or start_row

        ctx = self.set_context(options)
        ctx.update({'no_format':True, 'print_mode':True})
        lines = self.with_context(ctx).get_lines(options)
        if options.get('hierarchy'):
            lines = self.create_hierarchy(lines)
        max_width = 0
        if lines:
            max_width = max([len(l['columns']) for l in lines])

        num_table_col = len(self.get_columns_name(options))
        num_table_excel_col = (num_table_col - max_width) * x_merge + max_width

        if num_table_excel_col < 3 and x_merge < 2:
            x_merge = 2

        num_table_excel_col = (num_table_col - max_width) * x_merge + max_width

#         Todo in master: Try to put this logic elsewhere
        x = x_offset
        for super_col in super_columns.get('columns', []):
            cell_content = super_col.get('string', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
            if x_merge > 1:
                sheet.merge_range(start_row, x, start_row, x + (x_merge - 1), cell_content, super_col_style)
                x += x_merge
            else:
                sheet.write(start_row, x, cell_content, super_col_style)
                x += 1

        x = x_offset
        col_place = 1
        for column in self.get_columns_name(options):
            column_name = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
            if x_merge > 1 and (col_place <= (num_table_col - max_width) or column_name.strip() == ''):
                sheet.merge_range(y_offset, x, y_offset, x + (x_merge - 1), column_name, title_style)
                x += x_merge
            else:
                sheet.write(y_offset, x, column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' '), title_style)
                x += 1
            col_place += 1
        y_offset += 1

        for y in range(0, len(lines)):
            if lines[y].get('level') == 0:
                style = level_0_style
            elif lines[y].get('level') == 1:
                style = level_1_style
            elif lines[y].get('level') == 2:
                style = level_2_style
            elif lines[y].get('level') == 3:
                style = level_3_style
            else:
                style = def_style
  
            x = x_offset
            if lines[y].get('code'):
                if x_merge > 1:
                    sheet.merge_range(y + y_offset, x, y + y_offset, x + (x_merge - 1), lines[y]['code'], style)
                    x += x_merge
                else:
                    sheet.write(y + y_offset, x, lines[y]['code'], style)
                    x += 1
            if 'total' in lines[y].get('class', '') and (num_table_excel_col - len(lines[y]['columns'])) > 1:
                num_cell_report_code = 1 if lines[y].get('show_report_code', False) else 0
                num_cell_report_note = 1 if lines[y].get('show_report_note', False) else 0
                num_cell_total = num_table_excel_col - len(lines[y]['columns']) - num_cell_report_code - num_cell_report_note
                if num_cell_total >1:
                    sheet.merge_range(y + y_offset, x, y + y_offset, x + num_cell_total - 1, lines[y]['name'], style)
                else:
                    sheet.write(y + y_offset, x, lines[y]['name'], style)
                x += num_cell_total
            else:
                if x_merge > 1:
                    sheet.merge_range(y + y_offset, x, y + y_offset, x + (x_merge - 1), lines[y]['name'], style)
                    sheet.set_column(x, x, 40)
                    x += x_merge
                else:
                    sheet.write(y + y_offset, x, lines[y]['name'], style)
                    sheet.set_column(x, x, 40)
                    x += 1
  
            cols = x
            if lines[y].get('show_report_code', False):
                report_code = lines[y].get('report_code') and lines[y].get('report_code') or None
                if x_merge > 1:
                    sheet.merge_range(y + y_offset, x, y + y_offset, x + (x_merge - 1), report_code, report_code_style)
                    cols += x_merge
                else:
                    sheet.write(y + y_offset, cols, report_code, report_code_style)
                    cols += 1
            if lines[y].get('show_report_note', False):
                report_note = lines[y].get('report_note') and lines[y].get('report_note') or None
                if x_merge > 1:
                    sheet.merge_range(y + y_offset, x, y + y_offset, x + (x_merge - 1), report_note, style)
                    cols += x_merge
                else:
                    sheet.write(y + y_offset, cols, report_note, style)
                    cols += 1
  
            for x in range(1, max_width - len(lines[y]['columns']) + 1):
                sheet.write(y + y_offset, x, None, style)
            a = 0

            for x in range(cols, len(lines[y]['columns']) + cols):
                a += 1
                # if isinstance(lines[y]['columns'][x - 1], tuple):
                    # lines[y]['columns'][x - 1] = lines[y]['columns'][x - 1][0]

                if 'total' in lines[y].get('class', ''):
                    sheet.write(y + y_offset, x, lines[y]['columns'][a - 1].get('name', ''), style)
                else:
                    sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, lines[y]['columns'][a - 1].get('name', ''), style)
 
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
    
    def _get_super_columns(self, options):
        return {}
    
    def replace_class(self):
        return {b'o_af_reports_no_print': b'', b'table-responsive': b'', b'<a': b'<span', b'</a>': b'</span>'}
    
    def get_template_ref(self):
        if hasattr(self, 'template_ref'):
            return self.template_ref
        return ''
