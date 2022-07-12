# -*- coding: utf-8 -*-

from odoo import models, _


class ReportAccountAgedReceivable(models.AbstractModel):
    _name = "account.aged.receivable"
    _description = "Aged Receivable"
    _inherit = "account.aged.partner"

    def set_context(self, options):
        context = super(ReportAccountAgedReceivable, self).set_context(options)
        context['account_type'] = 'receivable'
        return context

    def get_report_name(self):
        return _("Aged Receivable")

    def get_templates(self):
        templates = super(ReportAccountAgedReceivable, self).get_templates()
        templates.update({
                'main_template': 'to_account_reports.template_aged_receivable_report',
                'line_template': 'to_account_reports.line_template_aged_receivable_report',
            })
        return templates

