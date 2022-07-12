import copy
import json
import io
import logging

from odoo import models, _
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from babel.dates import get_quarter_names
from odoo.tools.misc import formatLang, format_date, xlsxwriter
from odoo.tools import config

_logger = logging.getLogger(__name__)


class AccountReport(models.AbstractModel):
    _name = 'stock.report.abstract'
    _description = 'Stock Report'

    def get_options(self, previous_options=None):
        if not previous_options:
            previous_options = {}
        options = {}
        filter_list = [attr for attr in dir(self) if attr.startswith('filter_') and len(attr) > 7 and not callable(getattr(self, attr))]
        for element in filter_list:
            filter_name = element[7:]
            options[filter_name] = getattr(self, element)

        group_multi_company = self.env['ir.model.data'].xmlid_to_object('base.group_multi_company')
        if self.env.user.id in group_multi_company.users.ids:
            companies = self.env.companies.ids
            options['multi_company'] = [{'id': c.id, 'name': c.name, 'selected': True if c.id in companies else False} for c in self.env.user.company_ids]

        for key, value in options.items():
            if key in previous_options and value is not None and previous_options[key] is not None:
                options[key] = previous_options[key]

        product_category = self.env['product.category'].search([('property_cost_method', '!=', 'standard')])
        product_ids = self.env['product.product'].search([('categ_id', 'in', product_category.ids)])
        product_ids.read(['id', 'name', 'categ_id'])
        options['product_category'] = []
        for category in product_category:
            name = self.get_parent_name(category)
            product = [{'id': product_id.id, 'name': product_id.name} for product_id in product_ids if product_id.categ_id.id == category.id ]
            options['product_category'] += [{'id': category.id, 'name': name, 'product': product}]

        if self.env.user.has_group('stock.group_stock_multi_locations'):

            def _prepare_location_vals_list(domain):
                location_ids = self.env['stock.location'].search(domain)
                return [{'id': location_id.id, 'name': self.get_parent_location_name(location_id), 'warehouse_id': str(location_id.warehouse_id.id)} for
                                     location_id in location_ids]

            domain = [('usage', 'in', ('internal', 'transit'))]
            options['locations'] = _prepare_location_vals_list(domain)

            current_warehouse_id = options.get('current_warehouse_location', {}).get('warehouse_id', False)
            if current_warehouse_id:
                domain.append(('warehouse_id', '=', current_warehouse_id))
                options['current_locations'] = _prepare_location_vals_list(domain)

        if self.env.user.has_group('stock.group_stock_multi_warehouses'):
            options['warehouses'] = []
            warehouse_ids = self.env['stock.warehouse'].search([])
            options['warehouses'] += [{'id': warehouse_id.id, 'name': warehouse_id.name} for warehouse_id in
                                      warehouse_ids]

        return options

    # TO BE OVERWRITTEN
    def get_columns_name(self, options):
        return []

    # TO BE OVERWRITTEN
    def get_lines(self, options, line_id=None):
        return []

    # TO BE OVERWRITTEN
    def get_templates(self):
        return {
                'main_template': 'to_stock_age_report.main_template',
                'line_template': 'to_stock_age_report.line_template',
                 'search_template': 'to_stock_age_report.search_template',
                 'render_print_template': 'to_stock_age_report.main_template'
        }

    # TO BE OVERWRITTEN
    def get_report_name(self):
        return _('General Report')

    def get_report_filename(self, options):
        """The name that will be used for the file when downloading pdf,xlsx,..."""
        return self.get_report_name().lower().replace(' ', '_')

    def reverse(self, values):
        """Utility method used to reverse a list, this method is used during template generation in order to reverse periods for example"""
        if type(values) != list:
            return values
        else:
            inv_values = copy.deepcopy(values)
            inv_values.reverse()
        return inv_values

    def set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        ctx = self.env.context.copy()
        ctx['company_ids'] = [self.env.company.id]
        if options.get('multi_company'):
            company_ids = [c.get('id') for c in options['multi_company'] if c.get('selected')]
            ctx['company_ids'] = company_ids if len(company_ids) > 0 else [c.get('id') for c in options['multi_company']]
        return ctx

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self.get_options(options)
        options = self.apply_period_filter(options)
        searchview_dict = {'options': options, 'context': self.env.context}
        info = {'options': options,
                'context': self.env.context,
                'buttons': self.get_reports_buttons(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view']._render_template(self.get_templates().get('search_template', 'to_stock_age_report.search_template'), values=searchview_dict),
                }
        return info

    def format_qty(self, qty):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        format = '%.{precision}f'.format(precision=precision)
        return qty and format % qty or qty

    def format_valuation(self, valuation):
        format = '%.{precision}f'.format(precision=self.env.company.currency_id.decimal_places)
        return valuation and format % valuation or valuation

    def get_html(self, options, additional_context=None):
        '''
        return the html value of report, or html value of unfolded line
        * if line_id is set, the template used will be the line_template
        otherwise it uses the main_template. Reason is for efficiency, when unfolding a line in the report
        we don't want to reload all lines, just get the one we unfolded.
        '''
        templates = self.get_templates()
        report = {
            'name': self.get_report_name(),
            'company_name': self.env.company.name,
            }
        lines = self.with_context(self.set_context(options)).get_lines(options)

        rcontext = {'report': report,
                    'lines': {'columns_header': self.get_columns_name(options), 'lines': lines},
                    'options': options,
                    'context': self.env.context,
                    'model': self,
                    'format_qty': self.format_qty,
                    'format_valuation': self.format_valuation,
                }
        if additional_context and type(additional_context) == dict:
            rcontext.update(additional_context)
        render_template = templates.get('main_template', 'to_stock_age_report.main_template')
        html = self.env['ir.ui.view']._render_template(
            render_template,
            values=dict(rcontext),
        )
        return html

    def get_reports_buttons(self):
        return [{'name': _('Print PDF'), 'action': 'print_pdf'}, {'name': _('Export (XLSX)'), 'action': 'print_xlsx'}]

    def format_value(self, value, currency=False):
        if self.env.context.get('no_format'):
            return value
        currency_id = currency or self.env.company.currency_id
        if currency_id.is_zero(value):
            # don't print -0.0 in reports
            value = abs(value)
        res = formatLang(self.env, value, currency_obj=currency_id)
        return res

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

    def apply_period_filter(self, options):
        if options['periods']['filter'] == 'default':
            options['periods']['date'] = date.today().strftime(DF)
        return options

    def print_pdf(self, options):
        return {
                'type': 'ir_actions_af_report_stock_download',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'pdf',
                         'financial_id': self.env.context.get('id'),
                         }
                }

    def replace_class(self):
        """When printing pdf, we sometime want to remove/add/replace class for the report to look a bit different on paper
        this method is used for this, it will replace occurence of value key by the dict value in the generated pdf
        """
        return {b'o_af_reports_no_print': b'', b'table-responsive': b'', b'<a': b'<span', b'</a>': b'</span>'}

    def get_pdf(self, options, minimal_layout=True):
        # As the assets are generated during the same transaction as the rendering of the
        # templates calling them, there is a scenario where the assets are unreachable: when
        # you make a request to read the assets while the transaction creating them is not done.
        # Indeed, when you make an asset request, the controller has to read the `ir.attachment`
        # table.
        # This scenario happens when you want to print a PDF report for the first time, as the
        # assets are not in cache and must be generated. To workaround this issue, we manually
        # commit the writes in the `ir.attachment` table. It is done thanks to a key in the context.
        if not config['test_enable']:
            self = self.with_context(commit_assetsbundle=True)
        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.company,
            'template_ref': self.get_template_ref()
        }

        body = self.env['ir.ui.view']._render_template(
            self.get_templates().get('print_template', 'to_stock_age_report.print_template'),
            values=dict(rcontext),
        )
        body_html = self.with_context(print_mode=True).get_html(options)
        body = body.replace(b'<body class="o_af_reports_body_print">', b'<body class="o_af_reports_body_print">' + body_html)

        return self.env['ir.actions.report']._run_wkhtmltopdf(
            bodies=[body],
            header=None, footer=None,
            landscape=True,
            specific_paperformat_args={'data-report-margin-top': 10, 'data-report-header-spacing': 10}
        )

    def print_xlsx(self, options):
        return {
                'type': 'ir_actions_af_report_stock_download',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'xlsx',
                         'financial_id': self.env.context.get('id'),
                         }
                }

    def get_xlsx(self, options, response):
        to_date = options['periods']['date']
        no_of_ped = int(options['periods']['number_of_period'])
        period_length = int(options['periods']['period_length'])
        company_id = False
        if options.get('multi_company', False):
            company_id = [company for company in options['multi_company'] if company['selected'] == True]
            company_id = company_id[0]['name']
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(self.get_report_name()[:31])
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        worksheet.set_zoom(80)
        worksheet.set_column(0, 0, 40)
        worksheet.set_column(1, 1, 20)

        worksheet.set_column(2, (no_of_ped * 2) + 1, 20)

        # Add a bold format to use to highlight cells.
        title_report_format = workbook.add_format({'bold': True,
                                    'align':'center',
                                    'font_size': 25,
                                    'font_name': 'Times New Roman'})
        interval_format = workbook.add_format({'bold': True,
                                               'align':'left',
                                               'font_size': 20,
                                               'font_name': 'Times New Roman'})
        name_style_format = workbook.add_format({'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1,
                                           'align':'center',
                                           'valign': 'vcenter',
                                           'border': 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 12})
        content_cell_format = workbook.add_format({
            'border':1,
            'font_name': 'Times New Roman'
        })
        period_format = workbook.add_format({'bold': True,
                                             'font_size': 16,
                                             'align':'center',
                                             'border': 1,
                                             'valign': 'vcenter',
                                             'bg_color': 'cyan',
                                             'font_name': 'Times New Roman'})
        sum_row_cell_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'border':1,
            'font_name': 'Times New Roman'
        })
        worksheet.set_row(1, 30)
        title_report = [self.get_report_name()[:31]]
        worksheet.merge_range('A6:A7', _('Product Name'), name_style_format)
        worksheet.merge_range('B6:B7', _('Product Category'), name_style_format)

        sheet_title = []
        last_merge_col = 1
        for i in range(no_of_ped):
            if i == no_of_ped - 1:
                interval = '{} + '.format(period_length * i)
            else:
                interval = '{} - {}'.format(i * period_length, (i + 1) * period_length)
            sheet_title += [_("Q'ty On Hand"), _("Valuation")]
            worksheet.merge_range(5, last_merge_col + 1, 5, last_merge_col + 2, interval, period_format)
            last_merge_col = last_merge_col + 2

        worksheet.write_row(1, 4, title_report, title_report_format)
        worksheet.write_row(3, 2, [_('To Date:')], interval_format)
        worksheet.write(3, 3, to_date, interval_format)
        worksheet.write_row(3, 4, [_('Interval Days:')], interval_format)
        worksheet.write(3, 5, period_length, interval_format)
        worksheet.write_row(3, 6, [_('Company:')], interval_format)
        worksheet.write(3, 7, company_id or self.env.company.display_name, interval_format)
        worksheet.write_row(6, 2, sheet_title, name_style_format)
        worksheet.freeze_panes(7, 0)

        ctx = self.set_context(options)
        ctx.update({'no_format': True, 'print_mode': True})
        lines = self.with_context(ctx).get_lines(options)
        row = 7
        col = 0
        if lines:
            for items in lines:
                del items[0]
                if (row - 6) < len(lines):
                    del items[0]
                    for item in items:
                        worksheet.write(row, col, item, content_cell_format)
                        col += 1
                else:
                    col = 2
                    worksheet.write(row, col - 1, 'Summary', sum_row_cell_format)
                    for item in items:
                        worksheet.write(row, col, item, sum_row_cell_format)
                        col += 1
                row += 1
                col = 0
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def print_xml(self, options):
        return {
                'type': 'ir_actions_af_report_download',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'xml',
                         'financial_id': self.env.context.get('id'),
                         }
                }

    def get_xml(self, options):
        return False

    def print_txt(self, options):
        return {
                'type': 'ir_actions_af_report_download',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'txt',
                         'financial_id': self.env.context.get('id'),
                         }
                }

    def get_txt(self, options):
        return False

    def get_template_ref(self):
        if hasattr(self, 'template_ref'):
            return self.template_ref
        return ''
