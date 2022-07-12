# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    af_report_render_print_template = fields.Char(string='Account Report Print PDF Template', default='to_account_reports_l10n_vn.main_template_print_s200',
                                                  help='This template is only used when printing a financial report to a PDF output')
    coa_report_print_template = fields.Char(string='Trial Balance Report Print PDF Template', default='to_account_reports_l10n_vn.template_coa_report_print_s200')
    af_report_header_layout = fields.Char(string='Account Report Print PDF Header Layout', default='to_account_reports_l10n_vn.header_template_print_s200')
    af_report_footer_layout = fields.Char(string='Account Report Print PDF Footer Layout', default='to_l10n_vn_qweb_layout.accounting_external_footer_layout')

