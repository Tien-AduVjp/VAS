# -*- coding: utf-8 -*-
from odoo import models


class AccountReport(models.AbstractModel):
    _inherit = "account.report"

    def get_templates(self):
        res = super(AccountReport, self).get_templates()
        res.update({
            'header_layout': self.env.company.chart_template_id.sudo().af_report_header_layout or 'to_account_reports_l10n_vn.header_template_print_s200',
            'footer_layout': self.env.company.chart_template_id.sudo().af_report_footer_layout or 'to_l10n_vn_qweb_layout.accounting_external_footer_layout',
            'render_print_template': self.env.company.chart_template_id.sudo().af_report_render_print_template or 'to_account_reports_l10n_vn.main_template_print_s200'
            })
        return res
